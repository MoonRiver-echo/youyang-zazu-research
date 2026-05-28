/**
 * i18n.js — 国际化支持
 */

const I18n = (function() {
    const translations = {
        'zh-CN': {
            'site.title': '酉阳杂俎 · 神怪宗教文化',
            'site.subtitle': '唐段成式撰 — 数字人文研究',
            'common.loading': '加载中...',
            'nav.map': '地图',
            'nav.entries': '条目',
            'nav.culture': '文化',
            'nav.upload': '上传数据',
            'map.title': '地理分布',
            'map.desc': '酉阳杂俎所载神怪宗教事物的地理分布',
            'map.empty': '上传包含经纬度信息的 CSV 文件以显示地图',
            'map.hint': '支持包含 lat/lng 或 经度/纬度 列的数据',
            'entries.title': '条目浏览',
            'entries.search': '搜索条目...',
            'entries.allCategories': '全部分类',
            'entries.count': '共 {count} 条',
            'entries.empty': '暂无条目，上传 CSV 文件以填充数据',
            'entries.hint': '支持包含 name/title 列的数据',
            'culture.title': '文化关联',
            'culture.desc': '神怪宗教文化的类别分布与关联',
            'culture.distribution': '类别分布',
            'culture.timeline': '时代分布',
            'culture.catReligion': '宗教',
            'culture.catSupernatural': '神怪',
            'culture.catFolklore': '民俗',
            'culture.catGeography': '地理',
            'culture.catProducts': '物产',
            'culture.catRituals': '仪式',
            'culture.empty': '暂无文化数据，上传 CSV 文件以探索文化关联',
            'culture.hint': '支持包含 category/culture_type 列的数据',
            'upload.title': '上传数据',
            'upload.drag': '拖拽 CSV 文件到此处',
            'upload.or': '或',
            'upload.browse': '浏览文件',
            'upload.format': '支持 .csv 格式，建议包含 name, category, description, lat, lng, source, culture_type, period 列',
            'upload.preview': '数据预览',
            'upload.rows': '行',
            'upload.columns': '列',
            'upload.cancel': '取消',
            'upload.import': '导入数据',
            'footer.credit': '数字人文硕士学位毕业项目',
            'toast.importSuccess': '成功导入 {count} 条数据',
            'toast.importError': '导入失败，请检查文件格式',
            'toast.fileTypeError': '请上传 CSV 文件',
            'toast.noData': '暂无数据可显示'
        },
        'zh-TW': {
            'site.title': '酉陽雜俎 · 神怪宗教文化',
            'site.subtitle': '唐段成式撰 — 數字人文研究',
            'common.loading': '載入中...',
            'nav.map': '地圖',
            'nav.entries': '條目',
            'nav.culture': '文化',
            'nav.upload': '上傳資料',
            'map.title': '地理分布',
            'map.desc': '酉陽雜俎所載神怪宗教事物的地理分布',
            'map.empty': '上傳包含經緯度資訊的 CSV 檔案以顯示地圖',
            'map.hint': '支援包含 lat/lng 或 經度/緯度 欄位的資料',
            'entries.title': '條目瀏覽',
            'entries.search': '搜尋條目...',
            'entries.allCategories': '全部分類',
            'entries.count': '共 {count} 條',
            'entries.empty': '暫無條目，上傳 CSV 檔案以填充資料',
            'entries.hint': '支援包含 name/title 欄位的資料',
            'culture.title': '文化關聯',
            'culture.desc': '神怪宗教文化的類別分布與關聯',
            'culture.distribution': '類別分布',
            'culture.timeline': '時代分布',
            'culture.catReligion': '宗教',
            'culture.catSupernatural': '神怪',
            'culture.catFolklore': '民俗',
            'culture.catGeography': '地理',
            'culture.catProducts': '物產',
            'culture.catRituals': '儀式',
            'culture.empty': '暫無文化資料，上傳 CSV 檔案以探索文化關聯',
            'culture.hint': '支援包含 category/culture_type 欄位的資料',
            'upload.title': '上傳資料',
            'upload.drag': '拖曳 CSV 檔案到此處',
            'upload.or': '或',
            'upload.browse': '瀏覽檔案',
            'upload.format': '支援 .csv 格式，建議包含 name, category, description, lat, lng, source, culture_type, period 欄',
            'upload.preview': '資料預覽',
            'upload.rows': '行',
            'upload.columns': '欄',
            'upload.cancel': '取消',
            'upload.import': '匯入資料',
            'footer.credit': '數字人文碩士學位畢業專案',
            'toast.importSuccess': '成功匯入 {count} 筆資料',
            'toast.importError': '匯入失敗，請檢查檔案格式',
            'toast.fileTypeError': '請上傳 CSV 檔案',
            'toast.noData': '暫無資料可顯示'
        },
        'en': {
            'site.title': 'Youyang Zazu · Supernatural & Religious Culture',
            'site.subtitle': 'By Duan Chengshi, Tang Dynasty — Digital Humanities Research',
            'common.loading': 'Loading...',
            'nav.map': 'Map',
            'nav.entries': 'Entries',
            'nav.culture': 'Culture',
            'nav.upload': 'Upload Data',
            'map.title': 'Geographic Distribution',
            'map.desc': 'Geographic distribution of supernatural and religious records in Youyang Zazu',
            'map.empty': 'Upload a CSV file with latitude/longitude to display the map',
            'map.hint': 'Supports data with lat/lng or 经度/纬度 columns',
            'entries.title': 'Browse Entries',
            'entries.search': 'Search entries...',
            'entries.allCategories': 'All Categories',
            'entries.count': '{count} entries',
            'entries.empty': 'No entries yet. Upload a CSV file to populate data.',
            'entries.hint': 'Supports data with name/title columns',
            'culture.title': 'Cultural Associations',
            'culture.desc': 'Category distribution and associations of supernatural religious culture',
            'culture.distribution': 'Category Distribution',
            'culture.timeline': 'Temporal Distribution',
            'culture.catReligion': 'Religion',
            'culture.catSupernatural': 'Supernatural',
            'culture.catFolklore': 'Folklore',
            'culture.catGeography': 'Geography',
            'culture.catProducts': 'Products',
            'culture.catRituals': 'Rituals',
            'culture.empty': 'No cultural data yet. Upload a CSV file to explore associations.',
            'culture.hint': 'Supports data with category/culture_type columns',
            'upload.title': 'Upload Data',
            'upload.drag': 'Drag & drop a CSV file here',
            'upload.or': 'or',
            'upload.browse': 'Browse File',
            'upload.format': 'Supports .csv format. Recommended columns: name, category, description, lat, lng, source, culture_type, period',
            'upload.preview': 'Data Preview',
            'upload.rows': 'rows',
            'upload.columns': 'columns',
            'upload.cancel': 'Cancel',
            'upload.import': 'Import Data',
            'footer.credit': 'Digital Humanities Master\'s Thesis Project',
            'toast.importSuccess': 'Successfully imported {count} records',
            'toast.importError': 'Import failed. Please check the file format.',
            'toast.fileTypeError': 'Please upload a CSV file',
            'toast.noData': 'No data to display'
        }
    };

    let currentLang = 'zh-CN';

    function getLang() {
        return currentLang;
    }

    function setLang(lang) {
        if (translations[lang]) {
            currentLang = lang;
            updateDOM();
            document.documentElement.lang = lang;
            window.dispatchEvent(new CustomEvent('i18n:changed', { detail: { lang } }));
        }
    }

    function t(key, params = {}) {
        const dict = translations[currentLang] || translations['zh-CN'];
        let text = dict[key] || key;
        Object.keys(params).forEach(k => {
            text = text.replace(new RegExp(`{${k}}`, 'g'), params[k]);
        });
        return text;
    }

    function updateDOM() {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (key) el.textContent = t(key);
        });
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            if (key) el.placeholder = t(key);
        });
    }

    // Initialize
    document.addEventListener('DOMContentLoaded', () => {
        const saved = localStorage.getItem('youyang-lang');
        if (saved && translations[saved]) {
            currentLang = saved;
        }
        updateDOM();

        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const lang = btn.dataset.lang;
                setLang(lang);
                localStorage.setItem('youyang-lang', lang);

                document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });

        const activeBtn = document.querySelector(`.lang-btn[data-lang="${currentLang}"]`);
        if (activeBtn) {
            document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
            activeBtn.classList.add('active');
        }
    });

    return { getLang, setLang, t, updateDOM };
})();
