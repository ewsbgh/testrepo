const bind=(id,cb)=>{const el=document.getElementById(id);if(!el)return;cb(el.value);el.addEventListener('input',e=>cb(e.target.value));};
bind('slider1',v=>document.getElementById('g1').style.background=`linear-gradient(to top,#7B1E3A ${v*20}%,#f3e0db ${v*20}%)`);
bind('slider2',v=>document.getElementById('g2').style.opacity=String(1-(v-1)*0.15));
bind('slider3',v=>document.getElementById('g3').style.boxShadow=`0 0 ${v*3}px #FF6B4A`);
