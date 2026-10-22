
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Sky Bird — Flappy Adventure",
    page_icon="🐤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&display=swap');

.stApp {
    background: radial-gradient(ellipse at top, #243d70, #10172d 65%, #090f1d);
    font-family: 'Nunito', sans-serif;
}
header, footer, #MainMenu {visibility: hidden;}
.block-container {
    max-width: 1100px;
    padding: 1.5rem 1rem 0;
}
.hero {text-align:center; margin-bottom:20px;}
.hero h1 {
    font-size: clamp(36px, 5vw, 56px);
    font-weight: 900;
    letter-spacing: -2px;
    color: white;
    margin: 0;
    text-shadow: 0 5px 25px #65d8ff50;
}
.hero h1 span {color:#ffe16b;}
.hero p {color:#b9c9ed; margin-top:4px;}
.footer {
    color:#a8bbdf;
    text-align:center;
    padding:14px 0;
    font-size:13px;
}
div[data-testid="stExpander"] {
    background:#ffffff08;
    border:1px solid #ffffff22;
    border-radius:14px;
    color:white;
}
</style>
<div class="hero">
  <h1>SKY <span>BIRD</span> ✦</h1>
  <p>FLY HIGH · DODGE OBSTACLES · BEAT YOUR RECORD</p>
</div>
""", unsafe_allow_html=True)

html = r"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{box-sizing:border-box}
body{margin:0;background:transparent;font-family:Arial,sans-serif}
#gamebox{
 position:relative;width:100%;overflow:hidden;border-radius:22px;
 border:1px solid #ffffff70;
 box-shadow:0 25px 65px #0005,0 0 30px #5ee7ff18;
 background:#83ddff;
}
canvas{display:block;width:100%;height:auto;aspect-ratio:900/560;
 touch-action:manipulation;cursor:pointer}
#hud{
 position:absolute;top:15px;left:16px;right:16px;
 display:flex;justify-content:space-between;pointer-events:none
}
.stat{
 color:#c9ddff;font-size:10px;font-weight:bold;letter-spacing:1.5px;
 background:#13264caa;border:1px solid #ffffff50;
 border-radius:13px;padding:8px 16px;backdrop-filter:blur(8px)
}
.stat b{display:block;color:white;text-align:center;font-size:25px;
 letter-spacing:0}
#overlay{
 position:absolute;inset:0;display:flex;align-items:center;
 justify-content:center;background:#10264b24
}
#panel{
 width:min(84%,360px);text-align:center;color:white;padding:24px 22px;
 border-radius:24px;background:linear-gradient(145deg,#294777f5,#132443f2);
 border:1px solid #ffffff70;box-shadow:0 20px 55px #07142c66;
 backdrop-filter:blur(12px)
}
#birdicon{font-size:48px;animation:bob 1.5s ease-in-out infinite}
@keyframes bob{50%{transform:translateY(-8px) rotate(6deg)}}
#title{font-size:34px;font-weight:1000;margin:6px 0 8px}
#desc{font-size:13px;color:#d5e5ff;line-height:1.7;margin-bottom:18px}
#play{
 width:100%;padding:14px;border:0;border-radius:13px;
 background:linear-gradient(135deg,#fff29b,#ffc34d);
 color:#253451;font-size:14px;font-weight:900;letter-spacing:1px;
 box-shadow:0 5px 0 #bd8434;cursor:pointer
}
#play:active{transform:translateY(3px);box-shadow:none}
#hint{font-size:11px;color:#b7cbea;margin-top:15px}
</style>
</head>
<body>
<div id="gamebox">
 <canvas id="c" width="900" height="560"></canvas>
 <div id="hud">
  <div class="stat">BEST SCORE<b id="best">0</b></div>
  <div class="stat">YOUR SCORE<b id="score">0</b></div>
 </div>
 <div id="overlay">
  <div id="panel">
   <div id="birdicon">🐤</div>
   <div id="title">SKY BIRD</div>
   <div id="desc">Chinh phục bầu trời!<br>
   Bay qua những đường ống và phá kỷ lục của bạn.</div>
   <button id="play">✦ BẮT ĐẦU CHƠI ✦</button>
   <div id="hint">CLICK · SPACE · ↑ · CHẠM MÀN HÌNH</div>
  </div>
 </div>
</div>
<script>
(() => {
const c=document.getElementById('c'),ctx=c.getContext('2d');
const W=900,H=560,G=70,ground=H-G;
const $=id=>document.getElementById(id);
let mode='ready',score=0,best=0,frame=0,world=0,last=0;
let bird,pipes,particles,clouds,audio;

try{best=+(localStorage.getItem('skybird-best')||0)}catch(e){}
$('best').textContent=best;

function reset(){
 score=0;frame=0;pipes=[];particles=[];
 bird={x:230,y:240,vy:0,rot:0,wing:0};
 for(let i=0;i<3;i++)pipes.push(pipe(570+i*330));
 $('score').textContent=0;
}
function pipe(x){
 return {x,gapY:145+Math.random()*190,gap:166,scored:false};
}
function sound(f=600){
 try{
  audio=audio||new(window.AudioContext||window.webkitAudioContext)();
  const o=audio.createOscillator(),g=audio.createGain();
  o.connect(g);g.connect(audio.destination);o.frequency.value=f;
  g.gain.setValueAtTime(.04,audio.currentTime);
  g.gain.exponentialRampToValueAtTime(.001,audio.currentTime+.09);
  o.start();o.stop(audio.currentTime+.09);
 }catch(e){}
}
function burst(x,y,color,n=8){
 for(let i=0;i<n;i++)particles.push({
  x,y,vx:(Math.random()-.5)*5,vy:(Math.random()-.5)*5,
  life:25+Math.random()*15,size:2+Math.random()*3,color
 });
}
function start(){
 reset();mode='playing';$('overlay').style.display='none';flap();
}
function flap(){
 if(mode!=='playing')return;
 bird.vy=-6.7;burst(bird.x-10,bird.y+8,'#fff2a0',4);sound(550);
}
function action(){
 if(mode==='ready'||mode==='over')start();else flap();
}
c.addEventListener('pointerdown',e=>{e.preventDefault();action()});
$('play').addEventListener('click',start);
window.addEventListener('keydown',e=>{
 if(['Space','ArrowUp','KeyW'].includes(e.code)){
  e.preventDefault();if(!e.repeat)action();
 }
});
function ell(x,y,rx,ry,color){
 ctx.fillStyle=color;ctx.beginPath();
 ctx.ellipse(x,y,rx,ry,0,0,Math.PI*2);ctx.fill();
}
function round(x,y,w,h,r,color){
 ctx.fillStyle=color;ctx.beginPath();
 ctx.roundRect(x,y,w,h,r);ctx.fill();
}
function sky(){
 const g=ctx.createLinearGradient(0,0,0,H);
 g.addColorStop(0,'#40b5f1');g.addColorStop(.55,'#91e8ff');
 g.addColorStop(1,'#e1faff');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
 const glow=ctx.createRadialGradient(710,100,5,710,100,240);
 glow.addColorStop(0,'#fff9c9bb');glow.addColorStop(1,'#fff9c900');
 ctx.fillStyle=glow;ctx.fillRect(450,-100,460,400);
 ell(710,105,40,40,'#fff9d8');ell(710,105,31,31,'#fffef0');
 for(let i=0;i<24;i++){
  ctx.globalAlpha=.2+.2*Math.sin(frame*.03+i);
  ell((i*137+40)%W,(i*79+25)%310,2,2,'white');
 }
 ctx.globalAlpha=1;
}
function cloud(x,y,s){
 ctx.save();ctx.translate(x,y);ctx.scale(s,s);
 ell(0,12,47,16,'#ffffff35');
 ell(-22,0,22,18,'#ffffffc8');
 ell(0,-9,28,25,'#ffffffed');
 ell(26,3,24,17,'#ffffffdf');
 round(-28,0,62,17,8,'#ffffffdf');
 ctx.restore();
}
function landscape(){
 for(let l=0;l<2;l++){
  const step=250,off=(world*(l?.08:.15))%step;
  ctx.beginPath();ctx.moveTo(0,ground);
  for(let x=-step;x<W+step;x+=step){
   ctx.lineTo(x-off,(l?350:395)-50*Math.sin(x/180+l));
   ctx.lineTo(x+step/2-off,ground);
  }
  ctx.lineTo(W,ground);ctx.closePath();
  ctx.fillStyle=l?'#76c9cf':'#82bce0';ctx.globalAlpha=l?.45:.65;
  ctx.fill();ctx.globalAlpha=1;
 }
 ctx.beginPath();ctx.moveTo(0,ground);
 for(let x=0;x<=W;x+=8)
  ctx.lineTo(x,ground-26-16*Math.sin((x+world*.2)/130)-7*Math.sin(x/55));
 ctx.lineTo(W,ground);ctx.closePath();
 const g=ctx.createLinearGradient(0,ground-50,0,ground);
 g.addColorStop(0,'#8de19a');g.addColorStop(1,'#40b77a');
 ctx.fillStyle=g;ctx.fill();
}
function drawPipe(p){
 const x=p.x,w=76,top=p.gapY-p.gap/2,bottom=p.gapY+p.gap/2;
 const g=ctx.createLinearGradient(x,0,x+w,0);
 g.addColorStop(0,'#147b49');g.addColorStop(.25,'#65f49b');
 g.addColorStop(.55,'#24c76b');g.addColorStop(1,'#087442');
 // Pipe bodies
 round(x,-8,w,top+1,5,'#0d7046');
 ctx.fillStyle=g;ctx.fillRect(x+5,0,w-10,Math.max(0,top-7));
 ctx.fillStyle='#b6ffceaa';ctx.fillRect(x+13,0,6,Math.max(0,top-7));
 round(x-7,top-20,w+14,24,6,'#11844b');
 round(x-4,top-18,w+8,15,4,g);
 round(x,bottom,w,ground-bottom,5,'#0d7046');
 ctx.fillStyle=g;ctx.fillRect(x+5,bottom,w-10,Math.max(0,ground-bottom));
 ctx.fillStyle='#b6ffceaa';ctx.fillRect(x+13,bottom,6,Math.max(0,ground-bottom));
 round(x-7,bottom-4,w+14,24,6,'#11844b');
 round(x-4,bottom-2,w+8,15,4,g);
}
function drawGround(){
 ctx.fillStyle='#d9bc83';ctx.fillRect(0,ground,W,G);
 ctx.fillStyle='#5bc982';ctx.fillRect(0,ground,W,10);
 ctx.fillStyle='#a2f0a8';ctx.fillRect(0,ground,W,4);
 for(let x=-(world*.8%42);x<W;x+=42){
  ctx.fillStyle='#bba16d';
  ctx.beginPath();ctx.moveTo(x,ground+15);ctx.lineTo(x+17,ground+15);
  ctx.lineTo(x+2,ground+23);ctx.lineTo(x-12,ground+23);
  ctx.closePath();ctx.fill();
 }
}
function drawBird(){
 ctx.save();ctx.translate(bird.x,bird.y);ctx.rotate(bird.rot);
 ell(1,23,20,4,'#1d537522');
 ctx.fillStyle='#f49a2e';ctx.beginPath();
 ctx.moveTo(-17,0);ctx.lineTo(-30,-8);ctx.lineTo(-26,3);
 ctx.lineTo(-30,9);ctx.lineTo(-16,8);ctx.fill();
 const g=ctx.createLinearGradient(-15,-20,20,20);
 g.addColorStop(0,'#fff9a8');g.addColorStop(.5,'#ffdb4b');
 g.addColorStop(1,'#ff9b30');
 ell(0,0,23,20,'#e88c2b');ell(0,-3,22,19,g);
 ell(5,8,13,9,'#fff0b2');
 ctx.save();ctx.translate(-5,3);ctx.rotate(Math.sin(bird.wing)*.6);
 ell(-2,2,12,9,'#e99b35');ell(-1,0,10,7,'#fff080');
 ctx.restore();
 ell(10,-8,7,9,'white');ell(12,-7,3,5,'#26364b');
 ell(13,-9,1.5,2,'white');
 ctx.fillStyle='#f47d35';ctx.beginPath();
 ctx.moveTo(17,0);ctx.lineTo(31,5);ctx.lineTo(17,10);
 ctx.closePath();ctx.fill();
 ell(15,5,4,2.5,'#ff9b79');
 ctx.restore();
}
function drawParticles(){
 for(let i=particles.length-1;i>=0;i--){
  const p=particles[i];p.x+=p.vx;p.y+=p.vy;p.vy+=.06;p.life--;
  ctx.globalAlpha=Math.max(0,p.life/40);
  ell(p.x,p.y,p.size,p.size,p.color);
  if(p.life<=0)particles.splice(i,1);
 }
 ctx.globalAlpha=1;
}
function die(){
 if(mode!=='playing')return;
 mode='over';sound(170);
 burst(bird.x,bird.y,'#ffdf68',22);
 const record=score>best;
 if(record){
  best=score;
  try{localStorage.setItem('skybird-best',String(best))}catch(e){}
 }
 $('best').textContent=best;
 $('birdicon').textContent=record&&score>0?'🏆':'💫';
 $('title').textContent='GAME OVER';
 $('desc').innerHTML=`Bạn đạt <b style="color:#ffe16b;font-size:25px">${score}</b> điểm!<br>`+
 (record&&score>0?'Kỷ lục mới! Quá tuyệt vời!':'Cố lên, bạn có thể làm tốt hơn!');
 $('play').textContent='↻ CHƠI LẠI';
 $('overlay').style.display='flex';
}
function update(dt){
 frame+=dt;bird.wing+=.25*dt;
 if(mode==='playing'){
  world+=3.2*dt;bird.vy+=.34*dt;bird.y+=bird.vy*dt;
  bird.rot=Math.max(-.45,Math.min(1.1,bird.vy*.07));
  for(const p of pipes){
   p.x-=3.2*dt;
   const top=p.gapY-p.gap/2,bottom=p.gapY+p.gap/2;
   if(!p.scored&&p.x+76<bird.x){
    p.scored=true;score++;$('score').textContent=score;
    sound(800);burst(bird.x,bird.y,'#fff4a1',7);
   }
   if(bird.x+14>p.x-5&&bird.x-14<p.x+81&&
     (bird.y-14<top||bird.y+14>bottom))die();
  }
  pipes=pipes.filter(p=>p.x>-100);
  if(pipes.length===0||pipes[pipes.length-1].x<600)
   pipes.push(pipe(930));
  if(bird.y-18<0||bird.y+18>ground)die();
 }else{
  world+=.35*dt;
  if(mode==='ready')bird.y=240+Math.sin(frame*.07)*9;
 }
 for(const cl of clouds){
  cl.x-=cl.speed*dt;
  if(cl.x<-120)cl.x=W+120;
 }
}
function render(){
 sky();clouds.forEach(cl=>cloud(cl.x,cl.y,cl.s));
 landscape();pipes.forEach(drawPipe);drawGround();drawBird();drawParticles();
}
function loop(t){
 const dt=Math.min((t-last)/16.67||1,2);last=t;
 update(dt);render();requestAnimationFrame(loop);
}
clouds=[
 {x:120,y:125,s:.75,speed:.18},
 {x:430,y:195,s:1.05,speed:.12},
 {x:760,y:230,s:.65,speed:.22},
 {x:940,y:110,s:.9,speed:.15}
];
reset();requestAnimationFrame(loop);
})();
</script>
</body>
</html>
"""

components.html(html, height=590, scrolling=False)

st.markdown("""
<div class="footer">
  🖱️ Click chuột &nbsp; · &nbsp; ⌨️ Space / ↑ / W
  &nbsp; · &nbsp; 📱 Chạm màn hình để bay
</div>
""", unsafe_allow_html=True)

with st.expander("🎮 HƯỚNG DẪN CHƠI"):
    st.markdown("""
    - **Bắt đầu:** Nhấn nút BẮT ĐẦU CHƠI.
    - **Điều khiển:** Click chuột, nhấn Space, ↑, W hoặc chạm màn hình.
    - **Mục tiêu:** Vượt qua các khe giữa những đường ống xanh.
    - **Thua cuộc:** Khi chạm ống nước, trần hoặc mặt đất.
    - **Kỷ lục:** Điểm cao nhất được lưu bằng localStorage của trình duyệt.
    """)
