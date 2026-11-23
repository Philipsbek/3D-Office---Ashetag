#!/bin/sh
# Renders each mock-up page in blender/mockups/src/*.html to blender/mockups/out/<name>.jpg (1600x900)
# using headless Chrome.   sh blender/mockups/render.sh [name ...]
cd "$(dirname "$0")"
mkdir -p out
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
TMPPNG="C:/Users/user/AppData/Local/Temp/mockup_shot.png"
names="${*:-landing business store app}"
for n in $names; do
  url="file:///$(cygpath -m "$PWD/src/$n.html" | sed 's/ /%20/g')"
  "$CHROME" --headless=new --hide-scrollbars --force-device-scale-factor=1 --window-size=1600,900 \
    --virtual-time-budget=5000 --user-data-dir="C:/Users/user/AppData/Local/Temp/chr-mock" \
    --screenshot="$TMPPNG" "$url" >/dev/null 2>&1
  python -c "from PIL import Image; Image.open(r'$TMPPNG').convert('RGB').save(r'out/$n.jpg', quality=90)"
  echo "rendered out/$n.jpg"
done
