(function(){
  // Expose core globals
  if (typeof SHAPES === 'undefined' || typeof commandSetShape !== 'function') {
    console.warn('[ui_commands] SHAPES or commandSetShape not found');
    return;
  }
  window.SHAPES = SHAPES;
  window.COLOR_SCHEMES = COLOR_SCHEMES;
  window.commandSetShape = commandSetShape;
  window.commandSetColor = commandSetColor;
  window.commandTriggerMorph = commandTriggerMorph;

  // WebSocket handler
  const ws = new WebSocket((location.protocol==='https:'?'wss':'ws') + '://' + location.host + '/ws');
  ws.addEventListener('open', () => console.log('[ui_commands] WS connected'));
  ws.addEventListener('message', evt => {
    console.log('[ui_commands] Received', evt.data);
    let msg;
    try { msg = JSON.parse(evt.data); } catch(e) { console.error('[ui_commands] Invalid JSON', evt.data); return; }
    const cmd = msg.command || msg.ack;
    const args = msg.args || [];
    switch (cmd) {
      case 'set_shape':
        commandSetShape(args[0]);
        break;
      case 'set_color':
        commandSetColor(args[0]);
        break;
      case 'trigger_morph':
        commandTriggerMorph(args[0]);
        break;
      default:
        console.warn('[ui_commands] Unknown command', cmd);
    }
  });
  window.wsUI = ws;

  // Build Test UI buttons
  function buildTestUI() {
    const shapesDiv = document.querySelector('#test-ui > div:nth-child(1)');
    const colorsDiv = document.querySelector('#test-ui > div:nth-child(2)');
    if (!shapesDiv || !colorsDiv) return;
    SHAPES.forEach(s => {
      const btn = document.createElement('button');
      btn.textContent = s.name;
      btn.style.margin = '0 4px';
      btn.addEventListener('click', () => {
        const shape = s.name.toLowerCase();
        console.log('[ui_commands] Test set_shape', shape);
        commandSetShape(shape);
        ws.send(JSON.stringify({command:'set_shape', args:[shape]}));
      });
      shapesDiv.appendChild(btn);
    });
    Object.keys(COLOR_SCHEMES).forEach(name => {
      const btn = document.createElement('button');
      btn.textContent = name;
      btn.style.margin = '0 4px';
      btn.addEventListener('click', () => {
        console.log('[ui_commands] Test set_color', name);
        commandSetColor(name);
        ws.send(JSON.stringify({command:'set_color', args:[name]}));
      });
      colorsDiv.appendChild(btn);
    });
  }
  window.addEventListener('load', buildTestUI);
  setTimeout(buildTestUI, 500);
})();