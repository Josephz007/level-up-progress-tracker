#!/bin/bash
# Create Level Up.app macOS bundle from project files
# Usage: bash create_desktop_app.sh

set -e

APP_NAME="Level Up.app"
BUNDLE_DIR="$APP_NAME/Contents"
RESOURCES_DIR="$BUNDLE_DIR/Resources"
MACOS_DIR="$BUNDLE_DIR/MacOS"

# Clean up any old bundle
if [ -d "$APP_NAME" ]; then
    echo "Removing old $APP_NAME..."
    rm -rf "$APP_NAME"
fi

# Create directory structure
mkdir -p "$RESOURCES_DIR"
mkdir -p "$MACOS_DIR"

# Copy icon
cp levelup_logo.png "$RESOURCES_DIR/icon.png"

# Copy launcher scripts
cat > "$MACOS_DIR/launcher" <<'EOF'
#!/bin/bash
APP_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$APP_DIR/Contents/Resources"
if [ -f "$HOME/opt/anaconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/opt/anaconda3/etc/profile.d/conda.sh"
    conda activate tf 2>/dev/null || true
fi
python3 launch_desktop.py
EOF
chmod +x "$MACOS_DIR/launcher"

# Copy Python launcher
cp launch_desktop.py "$RESOURCES_DIR/launch_desktop.py"

# Create Info.plist
cat > "$BUNDLE_DIR/Info.plist" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.levelup.tracker</string>
    <key>CFBundleName</key>
    <string>Level Up Tracker</string>
    <key>CFBundleDisplayName</key>
    <string>Level Up Tracker</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.10</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>CFBundleIconFile</key>
    <string>icon.png</string>
</dict>
</plist>
EOF

# Done
open "$APP_NAME"
echo "✅ $APP_NAME created and opened!" 