#!/usr/bin/env python3
import urllib.request, gzip, json, hashlib, re, xml.etree.ElementTree as ET
from datetime import datetime, timezone

# region values: "Global" | "Global (institusi terdaftar)" | "US only" | "US + terpilih" | "ID tersedia" | "Cek per negara"
CURATED = [
  # ---------- STUDENT / DEVELOPER ----------
  {"t":"GitHub Student Developer Pack","p":"GitHub","c":"Developer","d":"Selama student","pr":"$0","e":"Student verified","r":"Global","u":"https://education.github.com/pack","x":"Copilot Pro + 100+ tools (JetBrains, Canva, Namecheap, DigitalOcean credit). Verifikasi pakai email kampus atau foto kartu student — Indonesia diterima.","g":["student","developer","copilot"]},
  {"t":"JetBrains All Products Pack","p":"JetBrains","c":"Developer","d":"1 tahun (renew)","pr":"$0","e":"Student/Teacher","r":"Global","u":"https://www.jetbrains.com/community/education/#students","x":"IntelliJ IDEA Ultimate, PyCharm Pro, WebStorm, DataGrip. Renew tiap tahun selama masih student.","g":["student","ide"]},
  {"t":"Cursor Pro Student","p":"Cursor","c":"AI","d":"12 bulan","pr":"$0","e":"Student","r":"US + terpilih","u":"https://cursor.com/students","x":"AI code editor Pro 1 tahun. Awalnya US-only, bertahap dibuka ke negara lain — cek halaman resmi apakah negara kamu sudah masuk.","g":["ai","developer","student"]},
  {"t":"GitHub Copilot Free Trial","p":"GitHub","c":"Developer","d":"30 hari","pr":"$0 trial","e":"Umum","r":"Global","u":"https://github.com/features/copilot","x":"Trial 30 hari untuk semua. Ada juga Copilot Free tier (limit 2000 completion/bln) tanpa batas waktu.","g":["ai","developer"]},
  {"t":"Vercel Hobby + Pro Trial","p":"Vercel","c":"Developer","d":"Hobby gratis selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://vercel.com/pricing","x":"Hobby plan gratis permanen (cukup untuk portfolio & side project). Pro trial 14 hari.","g":["developer","hosting"]},
  {"t":"Cloudflare Free Plan","p":"Cloudflare","c":"Developer","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://www.cloudflare.com/plans/free/","x":"CDN, DNS, Workers 100k req/hari, Pages unlimited bandwidth, R2 10GB. Free tier paling generous.","g":["developer","hosting"]},
  {"t":"Oracle Cloud Always Free","p":"Oracle","c":"Developer","d":"Selamanya","pr":"$0","e":"Umum (butuh kartu verifikasi)","r":"Global","u":"https://www.oracle.com/cloud/free/","x":"2 VM ARM (4 vCPU, 24GB RAM total) gratis permanen + 200GB storage. Butuh kartu untuk verifikasi, tidak ditagih.","g":["developer","vps","cloud"]},
  {"t":"Google Cloud $300 Credit","p":"Google","c":"Developer","d":"90 hari","pr":"$300 credit","e":"Akun baru","r":"Global","u":"https://cloud.google.com/free","x":"$300 credit 90 hari + Always Free tier (e2-micro VM, 5GB storage) setelahnya.","g":["cloud","developer"]},
  {"t":"AWS Free Tier","p":"Amazon","c":"Developer","d":"12 bulan + always free","pr":"$0","e":"Akun baru","r":"Global","u":"https://aws.amazon.com/free/","x":"EC2 t2.micro 750 jam/bln selama 12 bulan, Lambda 1jt req/bln permanen.","g":["cloud","developer"]},
  {"t":"Azure for Students","p":"Microsoft","c":"Developer","d":"12 bulan","pr":"$100 credit","e":"Student (.edu / verifikasi)","r":"Global","u":"https://azure.microsoft.com/free/students/","x":"$100 credit tanpa kartu kredit + 25+ service gratis selamanya.","g":["cloud","student"]},
  {"t":"DigitalOcean $200 Credit","p":"DigitalOcean","c":"Developer","d":"60 hari","pr":"$200 credit","e":"Akun baru","r":"Global","u":"https://www.digitalocean.com/free-trial-offer","x":"$200 credit 60 hari. Gratis lewat GitHub Student Pack juga.","g":["cloud","vps"]},

  # ---------- AI ----------
  {"t":"Google Gemini (AI Pro untuk Student)","p":"Google","c":"AI","d":"12 bulan","pr":"$0","e":"Student 18+","r":"US + terpilih","u":"https://gemini.google/students/","x":"Gemini AI Pro + 2TB storage 1 tahun. Berlaku di US, Jepang, Brazil, Indonesia, Korea (daftar negara berubah — cek halaman resmi).","g":["ai","student","google"]},
  {"t":"Perplexity Pro Student","p":"Perplexity","c":"AI","d":"1-12 bulan","pr":"$0","e":"Student (email kampus)","r":"Cek per negara","u":"https://www.perplexity.ai/student","x":"Pro search + akses model frontier. Durasi & negara tergantung promo yang aktif; kadang bundle lewat operator seluler.","g":["ai","student"]},
  {"t":"ChatGPT Free Tier","p":"OpenAI","c":"AI","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://chatgpt.com/","x":"GPT-5 dengan limit, browsing, image gen terbatas. Plus $20/bln tidak punya trial permanen — hanya promo musiman.","g":["ai"]},
  {"t":"Claude Free Tier","p":"Anthropic","c":"AI","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://claude.ai/","x":"Claude gratis dengan limit harian. Pro kadang ada trial 7 hari lewat langganan mobile app.","g":["ai"]},
  {"t":"Google AI Studio (API gratis)","p":"Google","c":"AI","d":"Selamanya","pr":"$0","e":"Umum","r":"Global (beberapa negara dibatasi)","u":"https://aistudio.google.com/","x":"Gemini API free tier untuk developer — rate limit tapi tanpa biaya. Cara termurah bangun app AI.","g":["ai","developer","api"]},
  {"t":"Groq API Free Tier","p":"Groq","c":"AI","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://console.groq.com/","x":"Inference super cepat (Llama, Mixtral) gratis dengan rate limit. Tanpa kartu kredit.","g":["ai","api"]},
  {"t":"HuggingFace Free Tier","p":"HuggingFace","c":"AI","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://huggingface.co/pricing","x":"Spaces gratis (CPU), Inference API limit, unlimited public repo model/dataset.","g":["ai","developer"]},
  {"t":"Notion AI","p":"Notion","c":"AI","d":"Termasuk paket Edu","pr":"$0","e":"Student → gratis","r":"Global","u":"https://www.notion.com/product/ai","x":"Gratis penuh kalau akun Education. Non-student dapat trial responses terbatas.","g":["ai","productivity"]},

  # ---------- EDITING / CREATIVE ----------
  {"t":"DaVinci Resolve (Free)","p":"Blackmagic","c":"Editing","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://www.blackmagicdesign.com/products/davinciresolve","x":"Editing + color grading + audio level Hollywood, versi free sudah sangat lengkap. Tidak ada watermark.","g":["editing","video"]},
  {"t":"CapCut Pro Trial","p":"CapCut","c":"Editing","d":"7 hari","pr":"$0 trial","e":"Umum","r":"Global (fitur beda per negara)","u":"https://www.capcut.com/","x":"Trial Pro 7 hari. Versi free tetap kuat untuk konten pendek. Beberapa fitur AI dibatasi per region.","g":["editing","video"]},
  {"t":"Adobe Creative Cloud Student","p":"Adobe","c":"Editing","d":"7 hari trial, lalu ~60% off","pr":"Diskon student","e":"Student","r":"Global (harga per negara)","u":"https://www.adobe.com/creativecloud/buy/students.html","x":"Photoshop, Premiere Pro, After Effects, Illustrator. Trial 7 hari gratis, lanjut harga student.","g":["editing","student","adobe"]},
  {"t":"CapCut / Canva Video Free","p":"Canva","c":"Editing","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://www.canva.com/video-editor/","x":"Video editor browser gratis, tanpa install. Pro gratis kalau lewat jalur Education.","g":["editing","design"]},
  {"t":"Shotcut / Kdenlive","p":"Open Source","c":"Editing","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://shotcut.org/","x":"Editor video open source, tanpa akun & tanpa watermark. Alternatif kalau tidak mau langganan.","g":["editing","opensource"]},
  {"t":"Audacity","p":"Open Source","c":"Editing","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://www.audacityteam.org/","x":"Audio editing & recording gratis penuh.","g":["editing","audio","opensource"]},

  # ---------- DESIGN ----------
  {"t":"Figma Education","p":"Figma","c":"Design","d":"Selama student","pr":"$0","e":"Student/Educator","r":"Global","u":"https://www.figma.com/education/","x":"Figma Professional + FigJam gratis. Verifikasi dokumen student, Indonesia diterima.","g":["student","design"]},
  {"t":"Canva Pro for Education","p":"Canva","c":"Design","d":"Selama terdaftar","pr":"$0","e":"Guru & siswa K-12 / kampus mitra","r":"Global (institusi terdaftar)","u":"https://www.canva.com/education/","x":"Canva Pro penuh. Untuk siswa harus diundang guru; guru bisa apply sendiri.","g":["student","design"]},
  {"t":"Autodesk Education","p":"Autodesk","c":"Design","d":"1 tahun (renew)","pr":"$0","e":"Student/Educator","r":"Global","u":"https://www.autodesk.com/education/edu-software/overview","x":"AutoCAD, Fusion 360, Maya, Revit, 3ds Max gratis 1 tahun, bisa perpanjang.","g":["student","design","3d"]},
  {"t":"Blender","p":"Blender Foundation","c":"Design","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://www.blender.org/","x":"3D modeling, animasi, VFX, video editing. Gratis penuh, tanpa lisensi.","g":["design","3d","opensource"]},
  {"t":"Framer Pro Trial","p":"Framer","c":"Design","d":"14 hari","pr":"$0 trial","e":"Umum","r":"Global","u":"https://www.framer.com/pricing","x":"Website builder visual. Free tier ada (subdomain framer.website).","g":["design","web"]},
  {"t":"Affinity Suite Trial","p":"Canva/Affinity","c":"Design","d":"6 bulan trial","pr":"$0 trial","e":"Umum","r":"Global","u":"https://affinity.serif.com/","x":"Photo, Designer, Publisher. Trial panjang + harga sekali bayar (tanpa langganan).","g":["design","editing"]},

  # ---------- PRODUCTIVITY ----------
  {"t":"Notion for Education","p":"Notion","c":"Productivity","d":"Selama student","pr":"$0","e":"Student/Educator (email kampus)","r":"Global","u":"https://www.notion.com/product/notion-for-education","x":"Notion Plus + Notion AI gratis. Verifikasi otomatis pakai email .edu / .ac.id.","g":["student","productivity"]},
  {"t":"Microsoft 365 Education","p":"Microsoft","c":"Productivity","d":"Selama terdaftar","pr":"$0","e":"Student kampus terdaftar","r":"Global (institusi terdaftar)","u":"https://www.microsoft.com/education/products/office","x":"Word, Excel, PowerPoint, Teams + 1TB OneDrive. Kampus harus punya lisensi institusi.","g":["student","office"]},
  {"t":"Google Workspace for Education","p":"Google","c":"Productivity","d":"Selama terdaftar","pr":"$0","e":"Lewat institusi","r":"Global (institusi terdaftar)","u":"https://edu.google.com/workspace-for-education/","x":"Classroom, Docs, Meet. Storage pool institusi.","g":["student","office"]},
  {"t":"Grammarly Free + Trial","p":"Grammarly","c":"Productivity","d":"Free selamanya / 7 hari Premium","pr":"$0","e":"Umum","r":"Global","u":"https://www.grammarly.com/","x":"Grammar checker gratis. Premium trial 7 hari lewat promo.","g":["productivity","ai"]},
  {"t":"Obsidian","p":"Obsidian","c":"Productivity","d":"Selamanya","pr":"$0","e":"Personal use","r":"Global","u":"https://obsidian.md/","x":"Note-taking lokal (markdown), gratis untuk penggunaan pribadi termasuk komersial-solo.","g":["productivity","notes"]},
  {"t":"Todoist Pro for Students","p":"Todoist","c":"Productivity","d":"Diskon/promo","pr":"Diskon student","e":"Student","r":"Cek per negara","u":"https://www.todoist.com/help/articles/student-discount","x":"Diskon Pro untuk student. Free tier sudah cukup untuk kebanyakan orang.","g":["productivity","student"]},

  # ---------- EDUCATION ----------
  {"t":"Coursera Plus Trial","p":"Coursera","c":"Education","d":"7 hari","pr":"$0 trial","e":"Umum","r":"Global","u":"https://www.coursera.org/courseraplus","x":"7 hari akses 10.000+ course. Banyak course bisa di-audit gratis tanpa sertifikat.","g":["education"]},
  {"t":"Coursera Financial Aid","p":"Coursera","c":"Education","d":"180 hari per course","pr":"$0","e":"Semua (isi form)","r":"Global","u":"https://www.coursera.support/s/article/209819033-Apply-for-Financial-Aid","x":"Sertifikat gratis lewat financial aid. Approval ~15 hari, tulis esai singkat.","g":["education","student"]},
  {"t":"freeCodeCamp","p":"freeCodeCamp","c":"Education","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://www.freecodecamp.org/","x":"Sertifikasi full-stack, Python, data science — 100% gratis tanpa paywall.","g":["education","developer"]},
  {"t":"Google Skills / Cloud Skills Boost","p":"Google","c":"Education","d":"Sering ada credit gratis","pr":"$0","e":"Umum","r":"Global","u":"https://www.cloudskillsboost.google/","x":"Lab hands-on GCP. Sering ada campaign credit gratis 30-90 hari.","g":["education","cloud"]},
  {"t":"MIT OpenCourseWare","p":"MIT","c":"Education","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://ocw.mit.edu/","x":"Materi kuliah MIT lengkap (video, PSet, solusi). Tanpa sertifikat.","g":["education"]},
  {"t":"Duolingo Free","p":"Duolingo","c":"Education","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://www.duolingo.com/","x":"Belajar bahasa gratis dengan iklan. Super trial 14 hari.","g":["education","language"]},

  # ---------- MUSIC / ENTERTAINMENT ----------
  {"t":"Spotify Premium Student","p":"Spotify","c":"Music","d":"1 bulan trial + 50% off","pr":"~Rp 27rb/bln","e":"Student kampus terverifikasi","r":"ID tersedia","u":"https://www.spotify.com/student/","x":"Diskon 50%. Verifikasi lewat SheerID; kampus Indonesia banyak yang sudah terdaftar.","g":["music","student"]},
  {"t":"Apple Music Student","p":"Apple","c":"Music","d":"1 bulan trial + diskon","pr":"~Rp 35rb/bln","e":"Student","r":"ID tersedia","u":"https://www.apple.com/apple-music/","x":"Harga student + Apple TV+ termasuk di beberapa region.","g":["music","student"]},
  {"t":"YouTube Premium Student","p":"Google","c":"Music","d":"1 bulan trial + diskon","pr":"~Rp 35rb/bln","e":"Student","r":"ID tersedia","u":"https://www.youtube.com/premium/student","x":"No-ads + YouTube Music. Verifikasi ulang tahunan, maks 4 tahun.","g":["music","student"]},
  {"t":"Amazon Prime Student","p":"Amazon","c":"Entertainment","d":"6 bulan gratis","pr":"$0","e":"Student","r":"US/UK/EU","u":"https://www.amazon.com/prime/student","x":"6 bulan Prime gratis lalu 50% off. Tidak berlaku Indonesia.","g":["student","shopping"]},

  # ---------- SECURITY / VPN / MISC ----------
  {"t":"Proton Free (Mail/VPN/Drive)","p":"Proton","c":"Privacy","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://proton.me/","x":"Email terenkripsi 1GB, VPN gratis unlimited data (server terbatas), Drive 5GB.","g":["privacy","vpn"]},
  {"t":"Cloudflare WARP","p":"Cloudflare","c":"Privacy","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://one.one.one.one/","x":"VPN-ish (1.1.1.1) gratis unlimited, bukan untuk ganti lokasi negara.","g":["privacy","vpn"]},
  {"t":"Bitwarden Free","p":"Bitwarden","c":"Privacy","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://bitwarden.com/","x":"Password manager gratis unlimited device & unlimited password. Open source.","g":["privacy","security"]},
  {"t":"Namecheap .me Domain","p":"Namecheap","c":"Developer","d":"1 tahun","pr":"$0","e":"Lewat GitHub Student Pack","r":"Global","u":"https://education.github.com/pack/offers","x":"Domain .me gratis 1 tahun + SSL. Klaim dari GitHub Student Pack.","g":["student","domain"]},
  {"t":"Windscribe Free 10GB","p":"Windscribe","c":"Privacy","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://windscribe.com/","x":"VPN 10GB/bulan gratis kalau konfirmasi email, 10+ lokasi negara. Bisa ganti region.","g":["vpn","privacy"]},
  {"t":"Tailscale Personal","p":"Tailscale","c":"Privacy","d":"Selamanya","pr":"$0","e":"Personal use","r":"Global","u":"https://tailscale.com/pricing","x":"Mesh VPN gratis 3 user + 100 device. Cara termudah akses VPS/homelab tanpa buka port.","g":["vpn","developer","privacy"]},

  # ---------- HOSTING / DATABASE ----------
  {"t":"Supabase Free Tier","p":"Supabase","c":"Hosting","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://supabase.com/pricing","x":"Postgres 500MB, auth, storage 1GB, realtime. Project di-pause kalau idle 1 minggu.","g":["database","backend","developer"]},
  {"t":"Neon Free Tier","p":"Neon","c":"Hosting","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://neon.com/pricing","x":"Serverless Postgres 0.5GB, branching database (bikin cabang DB kayak git).","g":["database","developer"]},
  {"t":"MongoDB Atlas M0","p":"MongoDB","c":"Hosting","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://www.mongodb.com/pricing","x":"Cluster shared 512MB gratis permanen, tanpa kartu kredit.","g":["database","developer"]},
  {"t":"Upstash Free Tier","p":"Upstash","c":"Hosting","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://upstash.com/pricing","x":"Redis + Kafka serverless, bayar per request. Free tier 10k command/hari.","g":["database","developer"]},
  {"t":"Netlify Free","p":"Netlify","c":"Hosting","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://www.netlify.com/pricing/","x":"Static hosting 100GB bandwidth/bln + serverless function 125k req.","g":["hosting","developer"]},
  {"t":"GitHub Pages","p":"GitHub","c":"Hosting","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://pages.github.com/","x":"Hosting static dari repo, 100GB bandwidth/bln, custom domain + SSL gratis.","g":["hosting","developer"]},
  {"t":"Render Free Web Service","p":"Render","c":"Hosting","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://render.com/pricing","x":"Web service gratis (sleep setelah 15 menit idle) + static site unlimited.","g":["hosting","developer"]},
  {"t":"Resend Free 3000 Email","p":"Resend","c":"Hosting","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://resend.com/pricing","x":"3.000 email/bulan, 100/hari. API transactional email paling gampang dipakai.","g":["email","api","developer"]},
  {"t":"Cloudinary Free Tier","p":"Cloudinary","c":"Hosting","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://cloudinary.com/pricing","x":"CDN gambar/video + transform on-the-fly, 25 credit/bln (~25GB bandwidth).","g":["media","developer"]},
  {"t":"GitHub Codespaces Free","p":"GitHub","c":"Developer","d":"Selamanya (kuota bulanan)","pr":"$0","e":"Akun personal","r":"Global","u":"https://github.com/features/codespaces","x":"120 core-hours + 15GB storage per bulan gratis. VS Code di browser, cocok tanpa laptop kuat.","g":["developer","cloud"]},
  {"t":"Postman Free","p":"Postman","c":"Developer","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://www.postman.com/pricing/","x":"API testing, 3 collaborator, unlimited collection & request.","g":["developer","api"]},

  # ---------- STORAGE ----------
  {"t":"MEGA 20GB Free","p":"MEGA","c":"Storage","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://mega.io/pricing","x":"20GB gratis dengan enkripsi end-to-end. Transfer quota dibatasi per hari.","g":["storage","privacy"]},
  {"t":"Google Drive 15GB","p":"Google","c":"Storage","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://one.google.com/about/plans","x":"15GB dibagi Drive + Gmail + Photos. Google One trial 1 bulan untuk upgrade.","g":["storage"]},
  {"t":"Backblaze B2 10GB","p":"Backblaze","c":"Storage","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://www.backblaze.com/cloud-storage/pricing","x":"Object storage S3-compatible 10GB gratis. Egress gratis kalau lewat Cloudflare.","g":["storage","developer"]},
  {"t":"Dropbox Basic 2GB","p":"Dropbox","c":"Storage","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://www.dropbox.com/plans","x":"2GB gratis, bisa nambah lewat referral. Sync paling stabil lintas OS.","g":["storage"]},

  # ---------- AUTOMATION / NO-CODE ----------
  {"t":"n8n Self-Hosted","p":"n8n","c":"Automation","d":"Selamanya","pr":"$0","e":"Self-host","r":"Global","u":"https://n8n.io/pricing/","x":"Workflow automation unlimited kalau host sendiri (Docker). Alternatif Zapier tanpa biaya.","g":["automation","opensource"]},
  {"t":"Zapier Free","p":"Zapier","c":"Automation","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://zapier.com/pricing","x":"100 task/bulan, 5 zap single-step. Cukup untuk automation ringan.","g":["automation"]},
  {"t":"Make Free","p":"Make","c":"Automation","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://www.make.com/en/pricing","x":"1.000 operation/bulan, 2 active scenario. Editor visual lebih fleksibel dari Zapier.","g":["automation"]},
  {"t":"Google Apps Script","p":"Google","c":"Automation","d":"Selamanya","pr":"$0","e":"Akun Google","r":"Global","u":"https://script.google.com/","x":"Automation Sheets/Gmail/Drive + trigger terjadwal. Gratis penuh, kuota harian wajar.","g":["automation","developer"]},

  # ---------- GAMING ----------
  {"t":"Epic Games Free Weekly","p":"Epic Games","c":"Gaming","d":"Rotasi tiap minggu","pr":"$0","e":"Umum","r":"Global","u":"https://store.epicgames.com/free-games","x":"1-2 game berbayar digratiskan tiap Kamis, klaim = milik permanen. Sudah ratusan game dibagi.","g":["gaming","deal"]},
  {"t":"Steam Free to Play","p":"Valve","c":"Gaming","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://store.steampowered.com/genre/Free%20to%20Play/","x":"Katalog F2P + demo. Steam Next Fest tiap kuartal ada ratusan demo gratis.","g":["gaming"]},
  {"t":"Unity Personal","p":"Unity","c":"Gaming","d":"Selamanya","pr":"$0","e":"Revenue < $200k/tahun","r":"Global","u":"https://unity.com/products/unity-personal","x":"Engine lengkap gratis sampai revenue $200k/tahun. Splash screen sudah opsional.","g":["gaming","developer"]},
  {"t":"Unreal Engine 5","p":"Epic Games","c":"Gaming","d":"Selamanya","pr":"$0 sampai $1jt revenue","e":"Umum","r":"Global","u":"https://www.unrealengine.com/download","x":"Gratis sampai game revenue $1jt, lalu royalti 5%. Non-game (film/arsitektur) gratis penuh.","g":["gaming","developer","3d"]},
  {"t":"Godot Engine","p":"Godot Foundation","c":"Gaming","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://godotengine.org/","x":"Engine 2D/3D open source MIT — tanpa royalti, tanpa splash, tanpa batas revenue.","g":["gaming","opensource"]},

  # ---------- MUSIC / AUDIO PRODUCTION ----------
  {"t":"FL Studio Trial","p":"Image-Line","c":"Music","d":"Tanpa batas waktu","pr":"$0 trial","e":"Umum","r":"Global","u":"https://www.image-line.com/fl-studio-download/","x":"Trial tanpa expiry — semua fitur jalan, cuma tidak bisa buka ulang project yang disave.","g":["music","audio"]},
  {"t":"Ableton Live Trial","p":"Ableton","c":"Music","d":"90 hari","pr":"$0 trial","e":"Umum","r":"Global","u":"https://www.ableton.com/en/trial/","x":"Trial penuh 90 hari (paling panjang di kelas DAW). Ada harga student ~40% off setelahnya.","g":["music","audio"]},
  {"t":"Reaper 60-Day Eval","p":"Cockos","c":"Music","d":"60 hari","pr":"$0 trial","e":"Umum","r":"Global","u":"https://www.reaper.fm/","x":"DAW ringan, eval 60 hari tanpa batasan fitur. Lisensi personal cuma $60 sekali bayar.","g":["music","audio"]},
  {"t":"BandLab","p":"BandLab","c":"Music","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://www.bandlab.com/","x":"DAW browser + mastering gratis unlimited + distribusi ke Spotify tanpa biaya.","g":["music","audio"]},

  # ---------- AI CREATIVE ----------
  {"t":"ElevenLabs Free","p":"ElevenLabs","c":"AI","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://elevenlabs.io/pricing","x":"10.000 karakter TTS/bulan, voice cloning di tier bayar. Kualitas suara terbaik saat ini.","g":["ai","audio"]},
  {"t":"Leonardo AI Free","p":"Leonardo","c":"AI","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://leonardo.ai/","x":"150 token/hari untuk generate gambar. Model fine-tune komunitas banyak.","g":["ai","design"]},
  {"t":"Suno Free","p":"Suno","c":"AI","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://suno.com/","x":"Generate lagu lengkap (vokal + instrumen), 50 credit/hari. Non-komersial di tier gratis.","g":["ai","music"]},
  {"t":"Windsurf / Codeium Free","p":"Codeium","c":"AI","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://windsurf.com/pricing","x":"AI autocomplete + chat gratis unlimited untuk individu. Alternatif Copilot tanpa bayar.","g":["ai","developer"]},

  # ---------- DESIGN OPEN SOURCE ----------
  {"t":"GIMP","p":"GNU","c":"Design","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://www.gimp.org/","x":"Photo editing raster, alternatif Photoshop. Gratis penuh tanpa akun.","g":["design","opensource"]},
  {"t":"Krita","p":"KDE","c":"Design","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://krita.org/","x":"Digital painting & ilustrasi, brush engine kelas pro. Gratis, dibiayai donasi.","g":["design","opensource"]},
  {"t":"Inkscape","p":"Inkscape","c":"Design","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://inkscape.org/","x":"Vector editor (SVG), alternatif Illustrator. Cocok untuk logo & aset web.","g":["design","opensource"]},

  # ---------- EDUCATION EXTRA ----------
  {"t":"Linux Foundation Free Courses","p":"Linux Foundation","c":"Education","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://training.linuxfoundation.org/resources/free-courses/","x":"~60 course gratis: Kubernetes, DevOps, blockchain, Linux dasar. Sertifikat berbayar terpisah.","g":["education","developer"]},
  {"t":"Kaggle Learn","p":"Kaggle","c":"Education","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://www.kaggle.com/learn","x":"Micro-course data science + notebook GPU 30 jam/minggu gratis.","g":["education","ai","data"]},
  {"t":"Microsoft Learn","p":"Microsoft","c":"Education","d":"Selamanya","pr":"$0","e":"Umum","r":"Global","u":"https://learn.microsoft.com/training/","x":"Learning path Azure, .NET, Power Platform + sandbox lab gratis.","g":["education","cloud"]},
]

FEEDS = [
  "https://dev.to/feed/tag/free",
  "https://dev.to/feed/tag/student",
  "https://dev.to/feed/tag/ai",
  "https://blog.google/technology/developers/rss/",
  "https://www.theverge.com/rss/index.xml",
  "https://feeds.feedburner.com/TechCrunch/",
  "https://openai.com/news/rss.xml",
  "https://blog.google/products/gemini/rss",
]

KEYWORDS = ["free","trial","student","discount","promo","gratis","education","giveaway","deal","offer","coupon","no cost","open source"]

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 FreeTrialTracker/1.0","Accept":"*/*"})
        resp = urllib.request.urlopen(req, timeout=20)
        data = resp.read()
        if resp.headers.get('Content-Encoding') == 'gzip':
            data = gzip.decompress(data)
        return data
    except Exception as e:
        print("feed fail " + url + " : " + str(e))
        return None

def parse(data):
    items = []
    try:
        root = ET.fromstring(data)
    except Exception:
        return items
    for it in root.findall(".//item"):
        t = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        desc = it.findtext("description") or ""
        if t and link:
            items.append((t, link, re.sub(r'<[^>]+>', '', desc).strip()[:220]))
    ns = "{http://www.w3.org/2005/Atom}"
    for e in root.findall(".//" + ns + "entry"):
        t = (e.findtext(ns + "title") or "").strip()
        le = e.find(ns + "link")
        link = (le.get("href") if le is not None else "") or ""
        summ = e.findtext(ns + "summary") or e.findtext(ns + "content") or ""
        if t and link:
            items.append((t, link.strip(), re.sub(r'<[^>]+>', '', summ).strip()[:220]))
    return items

def relevant(title):
    tl = title.lower()
    return len(tl) >= 12 and any(k in tl for k in KEYWORDS)

def sid(url):
    return hashlib.md5(url.encode()).hexdigest()[:12]

def region_class(r):
    """Bucket region detail into 3 filterable classes."""
    rl = r.lower()
    if "institusi" in rl:
        return "Butuh institusi"
    if rl.startswith("global"):
        return "Semua region"
    return "Region tertentu"

def build():
    seen, out_items = set(), []
    for c in CURATED:
        if c["u"] in seen:
            continue
        seen.add(c["u"])
        out_items.append({
            "id": sid(c["u"]), "title": c["t"], "provider": c["p"], "category": c["c"],
            "duration": c["d"], "price": c["pr"], "eligibility": c["e"], "region": c["r"],
            "region_class": region_class(c["r"]),
            "url": c["u"], "desc": c["x"], "tags": c["g"], "source": "curated",
        })
    curated_n = len(out_items)

    feeds_n = 0
    seen_titles = set(x["title"].lower() for x in out_items)
    for f in FEEDS:
        data = fetch(f)
        if not data:
            continue
        for t, link, desc in parse(data):
            if feeds_n >= 40:
                break
            if link in seen or t.lower() in seen_titles or not relevant(t):
                continue
            seen.add(link)
            seen_titles.add(t.lower())
            feeds_n += 1
            out_items.append({
                "id": sid(link), "title": t,
                "provider": link.split("/")[2] if "://" in link else "News",
                "category": "News/Deal", "duration": "—", "price": "—",
                "eligibility": "Umum", "region": "Cek per negara",
                "region_class": "Region tertentu",
                "url": link, "desc": desc, "tags": ["news"], "source": "feed",
            })

    regions = sorted(set(x["region"] for x in out_items))
    out = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(out_items), "curated": curated_n, "from_feeds": feeds_n,
        "regions": regions, "offers": out_items,
    }
    out["courses"] = out_items  # back-compat
    with open("data.json", "w") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print("Wrote data.json total=%d curated=%d feeds=%d regions=%d" % (len(out_items), curated_n, feeds_n, len(regions)))

    assert curated_n == len(CURATED), "curated dropped (duplicate URL?)"
    assert all(x.get("region") for x in out_items), "missing region"
    assert len(set(x["id"] for x in out_items)) == len(out_items), "duplicate id"

if __name__ == "__main__":
    build()
