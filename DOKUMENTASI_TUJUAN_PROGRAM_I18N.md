# Dokumentasi Internasionalisasi Tujuan Program

## Ringkasan
Semua deskripsi "Tujuan Program" di 10 Program Studi telah diinternasionalisasikan untuk mendukung 3 bahasa: Indonesia, Inggris, dan Mandarin (Simplified Chinese).

## Tanggal Implementasi
2 November 2025

## Perubahan yang Dilakukan

### 1. File yang Dimodifikasi
- **apps/pages/views.py**: Semua 10 fungsi `create_default_profile_page_*` telah diupdate

### 2. Program Studi yang Diupdate

| No | Program Studi | Function | Status |
|----|--------------|----------|---------|
| 1  | S1 Manajemen | `create_default_profile_page_manajemen()` | ✅ Complete |
| 2  | S2 Magister Manajemen | `create_default_profile_page_manajemens2()` | ✅ Complete |
| 3  | S1 Akuntansi | `create_default_profile_page_akuntansi()` | ✅ Complete |
| 4  | S1 Hospitaliti & Pariwisata | `create_default_profile_page_hospitality()` | ✅ Complete |
| 5  | S1 Fisika Medis | `create_default_profile_page_fisika_medis()` | ✅ Complete |
| 6  | S1 Teknik Informatika | `create_default_profile_page_teknik_informatika()` | ✅ Complete |
| 7  | S1 Statistika (Data Science) | `create_default_profile_page_statistika()` | ✅ Complete |
| 8  | S1 Desain Komunikasi Visual | `create_default_profile_page_dkv()` | ✅ Complete |
| 9  | S1 Arsitektur | `create_default_profile_page_arsitektur()` | ✅ Complete |
| 10 | S1 K3 | `create_default_profile_page_k3()` | ✅ Complete |

### 3. Struktur Data Sebelum dan Sesudah

#### Sebelum (Format Lama - Single Language):
```python
{
    'identifier': 'tujuan_section',
    'title': 'Tujuan',
    'description': 'Teks statis dalam Bahasa Indonesia...',
    'order': 4
}
```

#### Sesudah (Format Baru - Multilingual):
```python
{
    'identifier': 'tujuan_section',
    'title': {
        'id': 'Tujuan',
        'en': 'Objectives',
        'zh': '目标'
    },
    'description': {
        'id': 'Deskripsi dalam Bahasa Indonesia...',
        'en': 'Description in English...',
        'zh': '中文描述...'
    },
    'order': 4
}
```

## Fitur yang Didukung

### 1. Bahasa yang Tersedia
- **Indonesia (id)**: Bahasa utama dan fallback default
- **English (en)**: Bahasa Inggris  
- **Chinese (zh)**: Bahasa Mandarin (Simplified Chinese)

### 2. Mekanisme Fallback
Sistem akan secara otomatis fallback ke Bahasa Indonesia jika:
- Terjemahan untuk bahasa yang dipilih tidak tersedia
- Terjemahan kosong atau null
- Terjadi error dalam proses loading translation

### 3. Template Integration
Template `prodi.html` sudah mendukung multilingual content melalui:
- Attribute `data-i18n-content` untuk title
- Attribute `data-i18n-html` untuk description (mendukung HTML formatting)

## Cara Kerja Sistem

### 1. Frontend (JavaScript)
File `/static/js/i18n-content.js` menangani:
- Deteksi perubahan bahasa
- Loading content dari `window.pageBlocks`
- Update semua elemen dengan attribute `data-i18n-content` dan `data-i18n-html`
- Fallback otomatis ke Bahasa Indonesia

### 2. Backend (Django)
File `apps/pages/views.py`:
- Menyimpan data multilingual dalam ContentBlock sebagai JSON
- Format: `{field_name: {'id': '...', 'en': '...', 'zh': '...'}}`
- Data dikirim ke template melalui context `blocks`

### 3. Template (prodi.html)
Line 565-566:
```html
<h3 class="text-2xl font-bold text-matana-blue mb-6" 
    data-i18n-content="tujuan_section.title">
    {{ blocks.tujuan_section.title }}
</h3>
<div data-i18n-html="tujuan_section.description">
    {{ blocks.tujuan_section.description|safe|linebreaksbr }}
</div>
```

## Catatan Khusus

### 1. Lorem Ipsum Placeholder
Tiga program studi yang sebelumnya menggunakan placeholder Lorem Ipsum telah diganti dengan tujuan program yang sesuai:
- **Fisika Medis**: Tujuan fokus pada kompetensi di bidang fisika medis dan radiologi
- **Statistika**: Tujuan fokus pada analisis data dan statistika terapan
- **DKV**: Tujuan fokus pada kreativitas dalam desain komunikasi visual

### 2. Karakter Khusus
- Newline dalam teks menggunakan `\n` 
- Tab menggunakan `\t`
- Quote dalam string sudah di-escape dengan benar

### 3. Istilah Akademik
Beberapa istilah akademik tetap konsisten di semua bahasa:
- INTEGRITY / INTEGRITAS / 诚信
- STEWARDSHIP / PENATALAYANAN / 管理  
- RESPECT / SALING MENGHARGAI / 相互尊重
- RBTL (Research-Based Teaching and Learning)

## Cara Menambah/Mengubah Terjemahan

### 1. Via Django Admin
1. Login ke Django Admin
2. Navigasi ke Pages > Content Blocks
3. Filter berdasarkan identifier: `tujuan_section`
4. Edit content field (JSON format)
5. Update nilai untuk key yang diinginkan (`id`, `en`, atau `zh`)

### 2. Via Code
Edit file `apps/pages/views.py`, cari fungsi `create_default_profile_page_*` yang sesuai, update dictionary `description`:

```python
'description': {
    'id': 'Teks Indonesia baru...',
    'en': 'New English text...',
    'zh': '新的中文文本...'
}
```

## Testing

### 1. Test Language Switching
1. Buka halaman Program Studi (contoh: `/prodi-manajemen`)
2. Klik language selector di navbar (ID/EN/ZH)
3. Verifikasi tab "Tujuan Program" berubah bahasa dengan benar
4. Cek bahwa format dan line breaks tetap terjaga

### 2. Test Fallback
1. Hapus sementara salah satu translation (contoh: `en`)
2. Switch ke bahasa English
3. Verifikasi sistem fallback ke Bahasa Indonesia
4. Kembalikan translation yang dihapus

### 3. Test di Multiple Browser
- Chrome/Edge (Chromium)
- Firefox
- Safari (jika tersedia)

## Troubleshooting

### Masalah: Terjemahan Tidak Muncul
**Solusi:**
1. Clear browser cache (Ctrl+Shift+R)
2. Cek browser console untuk error JavaScript
3. Verifikasi `window.pageBlocks` ada di page source
4. Pastikan `i18n-content.js` ter-load dengan benar

### Masalah: Format/Line Breaks Hilang
**Solusi:**
1. Gunakan `\n` untuk newline dalam string
2. Pastikan template menggunakan `data-i18n-html` bukan `data-i18n-content`
3. Cek bahwa `|safe|linebreaksbr` filter digunakan di fallback content

### Masalah: Bahasa Tidak Persist
**Solusi:**
1. Cek localStorage di browser developer tools
2. Verifikasi `i18n-init.js` menghandle storage dengan benar
3. Clear localStorage dan test ulang

## Referensi

### Dokumentasi Terkait
- `README_PRODI_I18N.md`: Panduan implementasi multilingual untuk Program Studi
- `MULTILINGUAL_CONTENT_GUIDE.md`: Panduan teknis multilingual content
- `TRANSLATION_GUIDE.md`: Panduan untuk translator
- `example_prodi_content_multilingual.json`: Contoh struktur data multilingual

### File Sistem I18N
- `/static/js/i18n-init.js`: Inisialisasi sistem i18n
- `/static/js/i18n-content.js`: Handler untuk content switching
- `/static/locales/id.json`: Static translations (nav, footer, dll)
- `/static/locales/en.json`: Static translations English
- `/static/locales/zh.json`: Static translations Chinese

## Kontak & Support
Untuk pertanyaan atau issues terkait implementasi ini, silakan:
1. Buat issue di GitHub repository
2. Tag dengan label `i18n` dan `prodi`
3. Sertakan screenshot jika memungkinkan

---

**Version:** 1.0  
**Last Updated:** 2025-11-02  
**Author:** GitHub Copilot
