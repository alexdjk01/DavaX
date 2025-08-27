const form = document.getElementById('chat-form');
const input = document.getElementById('msg');
const box = document.getElementById('messages');

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
function canListen() {
  return !!SpeechRecognition;
}

const ttsToggle = document.getElementById('toggle-tts');
if (ttsToggle) {
  ttsToggle.checked = localStorage.getItem('autoTTS') === '1';
  ttsToggle.addEventListener('change', () => {
    localStorage.setItem('autoTTS', ttsToggle.checked ? '1' : '0');
    if (!ttsToggle.checked) stopSpeaking();
  });
}

const toggle = document.getElementById('toggle-details');
if (toggle) {
  // init from storage
  toggle.checked = localStorage.getItem('autoShowDetails') === '1';
  toggle.addEventListener('change', () => setAutoShowDetails(toggle.checked));
}

// --- TTS helpers ---
function canSpeak() {
  return 'speechSynthesis' in window;
}

function speak(text) {
  if (!canSpeak() || !text) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  // Optional: choose an English voice if available
  const voices = window.speechSynthesis.getVoices();
  const en = voices.find(v => /en-/i.test(v.lang));
  if (en) u.voice = en;
  window.speechSynthesis.speak(u);
}

function stopSpeaking() {
  if (canSpeak()) window.speechSynthesis.cancel();
}

function addMsg(text, bot=false){
  const div = document.createElement('div');
  div.className = 'msg' + (bot?' bot':'');
  div.textContent = (bot?'> ':'> You: ') + text;
  box.appendChild(div); box.scrollTop = box.scrollHeight;
}

form.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const text = input.value.trim(); if(!text) return; input.value='';
  addMsg(text,false);
  addMsg('typing…',true);
  try{
    const res = await fetch('http://localhost:8000/chat',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message:text, language:'ro'})
    });
    const data = await res.json();
    box.lastChild.remove();
    // Title (make bold)
    const titleDiv = document.createElement('div');
    titleDiv.className = 'msg bot';
    titleDiv.innerHTML = `<strong>${data.title}</strong>`;
    box.appendChild(titleDiv);
    box.scrollTop = box.scrollHeight;
    // Short summary (normal)
    addMsg(data.summary, true);
    addMsg(data.summary, true);
    // Auto TTS if enabled
    if (ttsToggle && ttsToggle.checked) {
       speak(`${data.title}. ${data.summary}`);
    }
    if (data.long_summary) {
      const details = document.createElement('details');
      details.className = 'details-block';
      details.addEventListener('toggle', () => {
        const on = details.hasAttribute('open');
        if (on && ttsToggle && ttsToggle.checked && data.long_summary) {
          speak(data.long_summary);
        }
      });
      const sum = document.createElement('summary');
      sum.textContent = 'Show details';
      sum.setAttribute('aria-label', 'Show long summary');

      const content = document.createElement('div');
      content.className = 'msg bot long-summary';
      content.textContent = data.long_summary;

      details.appendChild(sum);
      details.appendChild(content);
      box.appendChild(details);
      box.scrollTop = box.scrollHeight;

           // === Cover generation button ===
        const extras = document.getElementById('extras');
        if (extras) {
          const btn = document.createElement('button');
          btn.className = 'cover-btn';
          btn.textContent = '🎨 Generate cover';
          extras.innerHTML = ''; // clear previous buttons
          extras.appendChild(btn);

          btn.addEventListener('click', async () => {
            btn.disabled = true;
            btn.textContent = 'Generating…';
            try {
              const res = await fetch('http://localhost:8000/cover', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({
                  title: data.title,
                  summary: data.long_summary || data.summary,
                  style: 'vintage paperback, CRT palette (green/black), bold type'
                })
              });
              const cov = await res.json();
              // display image below the last bot message
              const img = document.createElement('img');
              img.className = 'cover-img';
              img.alt = `${data.title} — AI cover`;
              img.src = cov.data_url;
              box.appendChild(img);
              box.scrollTop = box.scrollHeight;
            } catch (e) {
              addMsg('Cover generation failed. Try again.', true);
            } finally {
              btn.textContent = '🎨 Generate cover';
              btn.disabled = false;
            }
          });
        }
    }
  }catch(err){
    box.lastChild.remove();
    addMsg('Network or server error.', true);
  }
});

const micBtn = document.getElementById('mic');
let recognizer = null;
let listening = false;

if (micBtn) {
  if (!canListen()) {
    micBtn.disabled = true;
    micBtn.title = "Speech recognition not supported in this browser";
  } else {
    recognizer = new SpeechRecognition();
    recognizer.lang = 'en-US';
    recognizer.interimResults = true;
    recognizer.continuous = false;

    recognizer.onresult = (e) => {
      let finalTrans = '';
      for (let i = 0; i < e.results.length; i++) {
        const res = e.results[i];
        if (res.isFinal) finalTrans += res[0].transcript;
      }
      if (finalTrans) {
        input.value = finalTrans.trim();
        // auto-submit on final result:
        form.requestSubmit();
      }
    };
    recognizer.onend = () => {
      listening = false;
      micBtn.textContent = '🎤';
      micBtn.disabled = false;
    };
    recognizer.onerror = () => {
      listening = false;
      micBtn.textContent = '🎤';
      micBtn.disabled = false;
    };

    micBtn.addEventListener('click', () => {
      if (listening) {
        recognizer.stop();
        return;
      }
      try {
        micBtn.textContent = '●'; // recording indicator
        micBtn.disabled = true;   // prevent double clicks
        listening = true;
        recognizer.start();
      } catch {
        listening = false;
        micBtn.textContent = '🎤';
        micBtn.disabled = false;
      }
    });
  }
}