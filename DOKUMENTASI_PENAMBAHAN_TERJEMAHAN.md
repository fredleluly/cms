# Dokumentasi: Cara Menambah dan Mereview Translation Keys

**Bahasa:** Bahasa Indonesia  
**Terakhir Diperbarui:** 2 November 2025  
**Audience:** Administrator Konten, Developer, Translator

## Daftar Isi

1. [Ringkasan](#ringkasan)
2. [Jenis-Jenis Konten yang Perlu Diterjemahkan](#jenis-jenis-konten)
3. [Cara Menambah Translation Keys](#cara-menambah-translation-keys)
4. [Cara Mereview Translation Keys](#cara-mereview-translation-keys)
5. [Checklist Kualitas Terjemahan](#checklist-kualitas-terjemahan)
6. [Troubleshooting](#troubleshooting)

---

## Ringkasan

Sistem internationalisasi (i18n) di CMS Matana University mendukung 3 bahasa:
- **ID** (Bahasa Indonesia) - Bahasa default
- **EN** (English/Inggris)
- **ZH** (Mandarin Chinese/中文)

Ada dua jenis konten yang perlu diterjemahkan:

### 1. **Konten Statis UI** (Label, Button, Menu)
- Disimpan di: `static/locales/{id,en,zh}.json`
- Digunakan dengan: `data-i18n="nav.profile"` di HTML
- Contoh: Nama menu, tombol, label form

### 2. **Konten Dinamis** (Dari Database)
- Disimpan di: ContentBlock JSON field di Django Admin
- Digunakan dengan: `data-i18n-content="hero_section.title"` di HTML
- Contoh: Judul program, deskripsi, misi, kurikulum

---

## Jenis-Jenis Konten

### Konten Statis UI

Konten UI yang sama di semua halaman. Contoh:

```json
// static/locales/id.json
{
  "nav": {
    "profile": "Profil",
    "study_programs": "Program Studi"
  },
  "prodi": {
    "register_now": "Daftar Sekarang",
    "learn_more": "Pelajari Lebih Lanjut"
  }
}
```

### Konten Dinamis (Database)

Konten spesifik per halaman Program Studi:

```json
// Di Django Admin, ContentBlock dengan identifier "hero_section"
{
  "title": {
    "id": "Informatika",
    "en": "Informatics",
    "zh": "信息学"
  },
  "description": {
    "id": "Program studi teknologi informasi",
    "en": "Information technology study program",
    "zh": "信息技术学习计划"
  }
}
```

---

## Cara Menambah Translation Keys

### A. Menambah Konten Statis UI

**Langkah 1: Identifikasi Key yang Dibutuhkan**

Tentukan hierarki key. Gunakan format: `section.subsection.key`

Contoh:
- `nav.profile` - Menu navigasi
- `prodi.register_now` - Tombol di halaman prodi
- `footer.contact` - Footer

**Langkah 2: Edit File Locales**

Edit ketiga file berikut:
- `static/locales/id.json` (Indonesia)
- `static/locales/en.json` (English)
- `static/locales/zh.json` (中文)

```json
// Tambahkan di section yang sesuai
{
  "prodi": {
    "new_key": "Teks Baru",  // di id.json
    "new_key": "New Text",    // di en.json
    "new_key": "新文本"        // di zh.json
  }
}
```

**Langkah 3: Gunakan di Template**

```html
<button data-i18n="prodi.new_key">Teks Baru</button>
```

**Langkah 4: Test**

1. Refresh halaman
2. Klik language switcher (ID/EN/ZH)
3. Pastikan teks berubah sesuai bahasa

### B. Menambah Konten Dinamis (Database)

**Langkah 1: Buka Django Admin**

1. Login ke Django Admin
2. Pilih Pages → Content Blocks
3. Cari ContentBlock untuk halaman Program Studi yang ingin diedit

**Langkah 2: Edit JSON Content**

Struktur untuk setiap field teks:

```json
{
  "field_name": {
    "id": "Teks Indonesia",
    "en": "English Text",
    "zh": "中文文本"
  }
}
```

**Contoh Lengkap: Hero Section**

```json
{
  "title": {
    "id": "Informatika",
    "en": "Informatics",
    "zh": "信息学"
  },
  "description": {
    "id": "Program studi yang mempersiapkan lulusan untuk menjadi profesional di bidang teknologi informasi.",
    "en": "A study program that prepares graduates to become professionals in information technology.",
    "zh": "一个旨在培养信息技术领域专业人才的学习计划。"
  },
  "background_image": "/static/images/prodi/hero.jpg",
  "items": [
    {
      "title": {
        "id": "Akreditasi",
        "en": "Accreditation",
        "zh": "认证"
      },
      "description": {
        "id": "A",
        "en": "A",
        "zh": "A"
      }
    }
  ]
}
```

**Catatan Penting:**
- Field non-teks (gambar, URL) tetap string biasa
- Array items: setiap item di-translate individual
- HTML tags bisa digunakan di description (gunakan `<br>` untuk line break)

**Langkah 3: Simpan dan Test**

1. Klik "Save" di Django Admin
2. Buka halaman Program Studi
3. Test dengan language switcher

---

## Cara Mereview Translation Keys

### Checklist Review Konten Statis UI

1. **Konsistensi Key**
   ```bash
   python3 check_i18n_keys.py
   ```
   Script ini mengecek apakah semua key ada di ketiga file bahasa.

2. **Konsistensi Istilah**
   - Gunakan istilah yang sama untuk konsep yang sama
   - Contoh: "Program Studi" → "Study Program" (bukan "Study Course")

3. **Grammar dan Spelling**
   - ID: Gunakan Bahasa Indonesia yang baik dan benar
   - EN: American English spelling
   - ZH: Simplified Chinese characters

### Checklist Review Konten Dinamis

1. **Struktur JSON**
   - Pastikan semua field teks memiliki 3 bahasa: `id`, `en`, `zh`
   - Gunakan `example_prodi_content_multilingual.json` sebagai referensi

2. **Konsistensi Panjang**
   - Terjemahan tidak harus sama panjangnya, tapi hindari perbedaan ekstrim
   - UI harus tetap rapi di semua bahasa

3. **Format dan HTML**
   - Pastikan HTML tags konsisten di semua bahasa
   - Contoh: Jika ID pakai `<br>`, EN dan ZH juga harus pakai

4. **Istilah Akademik**
   
   Gunakan istilah yang konsisten untuk terminologi akademik:

   | Indonesia | English | 中文 |
   |-----------|---------|------|
   | Program Studi | Study Program | 学习计划 |
   | Visi | Vision | 愿景 |
   | Misi | Mission | 使命 |
   | Akreditasi | Accreditation | 认证 |
   | Kurikulum | Curriculum | 课程 |
   | Konsentrasi | Concentration | 专业方向 |
   | Peluang Karir | Career Opportunities | 职业机会 |
   | Sarjana (S1) | Bachelor's Degree | 学士学位 |
   | Magister (S2) | Master's Degree | 硕士学位 |

---

## Checklist Kualitas Terjemahan

### Sebelum Publish

- [ ] **Semua field teks memiliki 3 terjemahan** (id, en, zh)
- [ ] **Tidak ada placeholder `[TRANSLATE]`** yang tersisa
- [ ] **Grammar dan spelling sudah dicek**
- [ ] **Istilah akademik konsisten** dengan glossary
- [ ] **HTML formatting konsisten** di semua bahasa
- [ ] **Tested dengan language switcher** - semua bahasa tampil benar
- [ ] **Layout tetap rapi** di semua bahasa (tidak overflow/broken)
- [ ] **Fallback ke Indonesia berfungsi** jika ada key yang hilang

### Review Periodik

Lakukan review berkala (misalnya setiap bulan):

1. **Audit Konsistensi**
   - Jalankan `check_i18n_keys.py`
   - Review istilah baru yang ditambahkan
   - Update glossary jika perlu

2. **User Feedback**
   - Kumpulkan feedback dari pengguna internasional
   - Update terjemahan yang kurang natural

3. **Update Dokumentasi**
   - Tambah istilah baru ke glossary
   - Update contoh-contoh jika ada perubahan struktur

---

## Troubleshooting

### 1. Teks Tidak Berubah Saat Ganti Bahasa

**Penyebab:**
- Key tidak ada di file locale
- JavaScript error di console

**Solusi:**
```bash
# 1. Cek apakah key ada di semua bahasa
python3 check_i18n_keys.py

# 2. Buka browser console (F12), cek error JavaScript

# 3. Pastikan atribut data-i18n atau data-i18n-content benar
```

### 2. Terjemahan Tidak Lengkap

**Penyebab:**
- Ada field yang belum diterjemahkan

**Solusi:**
```bash
# Gunakan migration script untuk identifikasi field yang hilang
python3 migrate_prodi_content.py --dry-run --program-slug prodi-informatika
```

### 3. Layout Berantakan di Bahasa Tertentu

**Penyebab:**
- Teks terlalu panjang untuk space yang tersedia

**Solusi:**
- Gunakan sinonim yang lebih pendek
- Adjust CSS jika perlu (misalnya, tambah line-clamp)
- Test di mobile dan desktop

### 4. Fallback Tidak Berfungsi

**Penyebab:**
- Key tidak ada di id.json
- JavaScript error

**Solusi:**
```javascript
// Cek di browser console
console.log(window.i18n.t('prodi.missing_key'));
// Seharusnya fallback ke bahasa Indonesia
```

### 5. JSON Invalid Setelah Edit

**Penyebab:**
- Syntax error di JSON (koma, kurung, tanda kutip)

**Solusi:**
```bash
# Validasi JSON
python3 -c "import json; print(json.load(open('static/locales/id.json')))"

# Atau gunakan online JSON validator
```

---

## Tools dan Resources

### Script yang Tersedia

1. **check_i18n_keys.py**
   - Mengecek konsistensi keys di semua file locale
   - Mendeteksi missing keys

2. **migrate_prodi_content.py**
   - Migrasi konten single-language ke multilingual
   - Dry-run mode untuk preview

### File Referensi

1. **example_prodi_content_multilingual.json**
   - Contoh lengkap struktur konten multilingual
   - Gunakan sebagai template

2. **ADMIN_MULTILINGUAL_GUIDE.md**
   - Panduan lengkap untuk administrator
   - Step-by-step untuk berbagai skenario

3. **MULTILINGUAL_CONTENT_GUIDE.md**
   - Dokumentasi teknis untuk developer
   - Penjelasan implementasi

### Online Tools

- **JSON Validator**: https://jsonlint.com/
- **Google Translate**: Untuk terjemahan awal (tetap perlu review manual)
- **DeepL**: Alternatif translator dengan hasil lebih natural

---

## Best Practices

### 1. Gunakan Hierarki Key yang Jelas

✅ **Good:**
```json
{
  "prodi": {
    "hero": {
      "title": "...",
      "subtitle": "..."
    },
    "mission": {
      "title": "...",
      "items": [...]
    }
  }
}
```

❌ **Bad:**
```json
{
  "prodi_hero_title": "...",
  "prodi_hero_subtitle": "...",
  "prodi_mission_title": "..."
}
```

### 2. Konsistensi Naming Convention

- Gunakan snake_case untuk key: `study_program`, bukan `studyProgram`
- Gunakan nama yang deskriptif: `register_now` bukan `btn1`

### 3. Terjemahan Natural, Bukan Literal

✅ **Natural:**
- EN: "Learn More"
- ZH: "了解更多"

❌ **Literal:**
- EN: "Study More"
- ZH: "学习更多"

### 4. Simpan Context untuk Translator

Untuk teks yang ambigu, tambah comment di JSON:

```json
{
  "prodi": {
    "lead": {
      "id": "Pimpin masa depan Anda",
      "en": "Lead your future",
      "zh": "引领您的未来",
      "_comment": "CTA text encouraging students to take control of their future"
    }
  }
}
```

---

## Workflow Standar

### Menambah Halaman Program Studi Baru

1. **Persiapan**
   - Kumpulkan konten dalam Bahasa Indonesia
   - Identifikasi konten yang perlu diterjemahkan

2. **Buat Content Blocks**
   - Gunakan `example_prodi_content_multilingual.json` sebagai template
   - Isi konten Bahasa Indonesia terlebih dahulu
   - Tambahkan `[TRANSLATE]` untuk EN dan ZH

3. **Terjemahkan**
   - Terjemahkan sendiri ATAU
   - Gunakan Google Translate/DeepL untuk draft awal
   - **WAJIB review manual untuk akurasi**

4. **Quality Check**
   - Jalankan checklist kualitas terjemahan
   - Test di browser dengan ketiga bahasa
   - Test di mobile dan desktop

5. **Publish dan Monitor**
   - Publish ke production
   - Monitor user feedback
   - Update jika ada perbaikan

---

## Kontak dan Support

### Untuk Pertanyaan Teknis
- Lihat `MULTILINGUAL_CONTENT_GUIDE.md`
- Cek browser console untuk error JavaScript

### Untuk Pertanyaan Konten
- Lihat `ADMIN_MULTILINGUAL_GUIDE.md`
- Gunakan `example_prodi_content_multilingual.json` sebagai referensi

### Untuk Kualitas Terjemahan
- Konsultasikan dengan native speaker jika memungkinkan
- Gunakan glossary istilah akademik yang konsisten

---

**Terakhir Diperbarui:** 2 November 2025  
**Versi:** 1.0  
**Maintainer:** Tim IT Matana University
