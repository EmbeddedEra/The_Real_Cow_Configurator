"""Offline browser integration: actual app with a mock Web Serial device.
Run: uv run --with playwright==1.62.0 python tests/browser_mode.py
Requires Playwright Chromium installed. No real USB device is accessed.
"""
from pathlib import Path
import http.server, threading, functools
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
MOCK=r'''
window.mock={kind:'unified',active:'NORMAL',saved:'NORMAL',pending:'NORMAL',busy:false,commands:[],dropSave:false,badMode:false};
let controller;
function emit(text) { controller.enqueue(new TextEncoder().encode(text)); }
const mockPort={
 async open(){ this.readable=new ReadableStream({start(c){controller=c;}});this.writable=new WritableStream({write(bytes){
  const c=new TextDecoder().decode(bytes).trim().slice(1,-1);mock.commands.push(c);
  if(c==='IDENTIFY')emit(mock.kind==='robot'?'COW_ROBOT_V4.8.4\r\n':mock.kind==='unified'?'COW_REMOTE_V6.16.0\r\n':'COW_REMOTE_V6.6.0\r\n');
  else if(c==='DUMP'){
   const base='ADDR=43:4F:57:41:44\r\nCHANNEL=76\r\nWORKING_HOUR=10\r\nPLAY_STOP_DELAY_MS=2000\r\nPIVOT_MAX=325\r\nSLOW_MAX=1000\r\nFAST_MAX=1000\r\nSLOW_MODE_MAX=150\r\n';
   // Deliberately split mid-line and delay beyond an early complete chunk.
   emit(base.slice(0,17));setTimeout(()=>emit(base.slice(17)),30);
   if(mock.kind==='unified'){
    setTimeout(()=>emit('ACTIVE_MODE='+mock.active+'\r\nMODE='+mock.pending+'\r\n'),80);
    setTimeout(()=>emit('SAVED_MODE='+mock.saved+'\r\nDUMP_END\r\n'),150);
   }
  } else if(c==='MOTOR_STATE')emit('MOTOR_RIGHT=0 MOTOR_LEFT=0 MOTOR_COW=0\r\n');
  else if(c==='SONAR_READ')emit('SONAR_RAW=123\r\n');
  else if(c.startsWith('MODE=')) {
   if(mock.busy)emit('MODE_BUSY\r\n');
   else if(mock.badMode)emit('MODE_ERROR\r\n');
   else {mock.pending=c.slice(5);emit(c+'\r\nSAVE_AND_RESTART_REQUIRED\r\n');}
  } else if(c==='SAVE'){
   if(mock.busy)emit('CONFIG_BUSY\r\n');
   else if(!mock.dropSave){mock.saved=mock.pending;if(mock.kind==='unified')emit('SAVE_OK\r\n');}
  } else if(c==='LOAD') {mock.pending=mock.saved;if(mock.kind==='unified')emit('LOAD_OK\r\n');}
  else if(c==='RESET') {mock.pending=mock.saved='NORMAL';if(mock.kind==='unified')emit('RESET_OK\r\n');}
  else if(/^(PIVOT_MAX|SLOW_MAX|FAST_MAX|SLOW_MODE_MAX)=/.test(c))emit(c+'\r\n');
 }});},async close(){}
};
Object.defineProperty(navigator,'serial',{value:{requestPort:async()=>mockPort,addEventListener(){}}});
'''
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':1100,'height':850})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.route('**/*',lambda route: route.continue_() if route.request.url.startswith(f'http://127.0.0.1:{server.server_port}/') else route.abort())
    page.add_init_script(MOCK)
    page.goto(f'http://127.0.0.1:{server.server_port}/')
    page.click('#connectBtn');page.wait_for_function('remoteModeSupported && !configOperation')
    assert page.locator('#mode').input_value()=='NORMAL'
    page.select_option('#mode','RECORDING');assert 'not saved' in page.inner_text('#remoteModeStatus')
    page.click('#saveBtn');page.wait_for_function('mock.saved==="RECORDING" && !configOperation')
    assert 'Restart' in page.inner_text('#msg') and 'Active: NORMAL' in page.inner_text('#remoteModeStatus')
    assert page.evaluate('mock.commands.includes("MODE=RECORDING")')
    # Reconnect after a simulated power cycle reports the newly active mode.
    page.click('#connectBtn');page.evaluate('mock.active=mock.saved');page.click('#connectBtn')
    page.wait_for_function('remoteModeSupported && !configOperation')
    assert 'Restart' not in page.inner_text('#remoteModeStatus')
    page.click('#resetBtn');page.wait_for_function('mock.saved==="NORMAL" && !configOperation')
    assert 'Restart' in page.inner_text('#msg') and 'Active: RECORDING' in page.inner_text('#remoteModeStatus')
    # Busy/invalid MODE never reaches SAVE or claims success.
    page.evaluate('mock.busy=true;mock.commands=[]');page.select_option('#mode','RECORDING');page.click('#saveBtn')
    page.wait_for_function('!configOperation && mock.commands.length>0')
    assert 'MODE_BUSY' in page.inner_text('#msg') and not page.evaluate('mock.commands.includes("SAVE")')
    page.evaluate('mock.busy=false;mock.badMode=true');page.click('#saveBtn')
    page.wait_for_function('!configOperation && document.getElementById("msg").textContent.includes("MODE_ERROR")')
    page.evaluate('mock.badMode=false;mock.dropSave=true');page.click('#saveBtn')
    page.wait_for_function('!configOperation && document.getElementById("msg").textContent.includes("timed out")',timeout=15000)
    assert page.evaluate('mock.saved')=='NORMAL'
    # Import enum validation, legacy files, and requested-mode-only export.
    page.click('#connectBtn');page.evaluate('mock.dropSave=false');page.click('#connectBtn')
    page.wait_for_function('remoteModeSupported && !configOperation')
    page.locator('#importFile').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':b'{"mode":"BAD"}'})
    page.wait_for_function('document.getElementById("msg").textContent.includes("Invalid operating mode")')
    page.locator('#importFile').set_input_files({'name':'mode.json','mimeType':'application/json','buffer':b'{"mode":"RECORDING"}'})
    page.wait_for_function('document.getElementById("mode").value==="RECORDING"')
    page.locator('#importFile').set_input_files({'name':'old.json','mimeType':'application/json','buffer':b'{"channel":"76"}'})
    page.wait_for_timeout(50);assert page.locator('#mode').input_value()=='RECORDING'
    with page.expect_download() as download:page.click('#exportBtn')
    import json
    exported=json.loads(Path(download.value.path()).read_text())
    assert exported['mode']=='RECORDING' and 'active_mode' not in exported and 'saved_mode' not in exported
    # Old recording firmware: hide mode; save must never send MODE.
    page.click('#connectBtn');page.evaluate('mock.kind="old";mock.dropSave=false;mock.commands=[]');page.click('#connectBtn')
    page.wait_for_function('connectedDeviceType==="remote" && !configOperation')
    assert page.locator('#remoteModeRow').is_hidden()
    page.click('#saveBtn');page.wait_for_function('!configOperation && mock.commands.includes("SAVE")')
    assert not page.evaluate('mock.commands.some(c=>c.startsWith("MODE="))')
    # A robot also has no mode control.
    page.click('#connectBtn');page.evaluate('mock.kind="robot"');page.click('#connectBtn')
    page.wait_for_function('connectedDeviceType==="robot" && !configOperation')
    assert page.locator('#remoteModeRow').is_hidden()
    result=page.evaluate("sendCmd('SONAR_READ',true,{delayMs:0,timeoutMs:120})")
    assert 'SONAR_RAW=123' in result
    page.evaluate('mock.commands=[];startMotorStateReading()');page.wait_for_timeout(1200)
    page.evaluate('stopMotorStateReading()')
    assert page.evaluate('mock.commands.length')<14
    assert page.evaluate('serialSession.error===null')
    assert not errors, errors
    browser.close()
server.shutdown()
print('PASS: fragmented USB, mode save/restart/reset, busy/error/missing ACK, legacy remote and robot compatibility')
