# prnt.sc-Scraper
A simple script that scrapes 'prnt.sc' for credit cards/crypto wallets/nudes....
### Installation
You need to have Tesseract installed. You can do so by going [HERE](https://github.com/UB-Mannheim/tesseract/wiki) and download file `tesseract-ocr-w64-setup.....exe`, this is a installer for tesseract developed by Google. By default it should install in path `C:\Program Files\Tesseract-OCR`, if so you don't have to specify the `-fe` flag when running the script.
If the installer didn't install tesseract at the default path, you will need to provide the `-fe` flag followed by the full path, ex. `python3 finder.py -fe C:\Program Files\Tesseract-OCR\tesseract.exe`
### Flag Info
> For more flag information just run `python3 finder.py -h` it will display a simple help menu.
### Known Bugs
When you sepecify the `-fe` flag with an path that has a space in in ex. `C:\Program Files` tesseract won't load properly. To fix this issue, you need to go to line `204` and change the default path for `tesseract.exe` (from `C:\\Program Files\\Tesseract-OCR\\tesseract` to your path (NOTE: There needs to be 2x `\`))
