

saya mau agar page nya bisa di edit di dashboard 
yang text saja dan beberapa gambar

gunakan json,  yang berisi data untuk page tersebut
misal:
contoh jsonya:

{
    "id": 1,
    "title": "Sejarah Matana",
    "content": "Universitas Matana mulai beroperasi pada bulan Agustus 2014, berlokasi di Matana University Tower dengan 10 Program Studi. Universitas Matana mendidik calon-calon eksekutif bisnis dan pemimpin masa depan dalam berbagai bidang ilmu, dengan memberi penekanan yang seimbang antara pengetahuan akademik, pengembangan kemampuan soft skills dan pembentukan karakter mahasiswa yang bersifat menyeluruh. Proses pembelajaran yang evidence-driven adalah karakteristik khusus Universitas Matana, dimana mahasiswa dan dosen akan berkolaborasi dalam pembelajaran berbasis-penelitian atau research-based-teaching and learning (RBTL) untuk mengkonstruksi pengetahuan dan keterampilan bukan menghafal konten buku-teks.Bagi Universitas Matana, mahasiswa adalah insan potensial dan aset sosial yang harus dikembangkan dan di dorong menjadi manusia yang berintegritas, melayani, dan menghargai manusia dan kemanusiaan.",
},
{
    "id": 2,
    "title": "Visi dan Misi",
    "content": "Visi Universitas Matana adalah menjadi universitas yang unggul dan berwawasan global, berintegritas, dan berdikari. Misi Universitas Matana adalah menghasilkan lulusan yang berwawasan global, berintegritas, dan berdikari, serta mampu berkontribusi dalam pembangunan masyarakat dan negara.",
}

agar di dashboard nya bisa di edit, gamapang tinggal pakai django as form tanpa looping

nah di dashboard nya buat sebuah sidebar misal: pages
nah di pages itu ada banyak list untuk page nya
misal: 
- profile 
    - profile matana
    - manajemen
    - mitra
- program studi
    - informatika
    - akuntansi
    - manajemen
- pendaftaran
- beasiswa


bisa di edit di dashboard nya, sesuai yang saya beri tahu tadi, pakai json , django as form tanpa looping di dashboard nya biar gampang
yang di edit di dashboard nya adalah text saja dan gambar url nya

nah di frondend nya biar saya jadi gampang tinggal misal:

```
<!-- Sejarah -->
<section class="py-20 bg-gray-50">
    <div class="container mx-auto px-4">
        <h2 class="text-3xl font-bold text-center mb-16 section-title">{{title atau apa pakai dict juga boleh atau}}</h2>
        
        <div class="max-w-4xl mx-auto">
            <div class="prose prose-lg mx-auto">
                <p class="text-gray-600 leading-relaxed mb-6">
                {{content text nya atau apa pakai dict juga boleh atau}}
                </p>
            </div>
        </div>
    </div>
</section>
```
gunakan Pages dan content blocks nya di models,
kalau ada yang kurang modelnya bisa di update

dan buatkan sebuah file json yang berisi data untuk page tersebut

