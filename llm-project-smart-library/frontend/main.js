const form = document.getElementById('chat-form');
const input = document.getElementById('msg');
const box = document.getElementById('messages');

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
    addMsg(`${data.title}`, true);
    addMsg(data.summary, true);
  }catch(err){
    box.lastChild.remove();
    addMsg('Network or server error.', true);
  }
});