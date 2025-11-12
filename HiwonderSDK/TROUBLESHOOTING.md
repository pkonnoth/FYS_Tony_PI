# Troubleshooting Guide

## Issue: Action Group Files Not Found

### Symptom
When running action group scripts, you see error messages like:
```
未能找到动作组文件:(),是否将动作组保存在目录:/home/pi/TonyPi/ActionGroups/stand_slow.d6a
```
(Translation: "Action group file not found. Should the action group be saved in directory: /home/pi/TonyPi/ActionGroups/stand_slow.d6a")

The robot doesn't move because the action files can't be found.

### Cause
The action group files (`.d6a` files) are located in a different directory than expected. The script was looking in `/home/pi/TonyPi/ActionGroups/` but the files are actually in `/home/pi/one/tonypi_pro/TonyPi/ActionGroups/`.

### Solution
The updated scripts now automatically search for action group files in multiple locations:
1. `/home/pi/TonyPi/ActionGroups/`
2. `/home/pi/one/tonypi_pro/TonyPi/ActionGroups/`
3. `/home/pi/tonypi_pro/TonyPi/ActionGroups/`

The script will automatically use whichever location contains the files.

### If You Still Have Issues

1. **Check if action files exist:**
   ```bash
   find /home/pi -name "*.d6a" -type f | head -5
   ```

2. **Check specific action files:**
   ```bash
   ls /home/pi/one/tonypi_pro/TonyPi/ActionGroups/go_forward.d6a
   ls /home/pi/one/tonypi_pro/TonyPi/ActionGroups/stand_slow.d6a
   ```

3. **Manually specify path in your code:**
   ```python
   import hiwonder.ActionGroupControl as AGC
   
   # Use the correct path
   AGC.runActionGroup('go_forward', times=5, 
                     path="/home/pi/one/tonypi_pro/TonyPi/ActionGroups/")
   ```

4. **Create a symlink (alternative solution):**
   ```bash
   # Create the expected directory if it doesn't exist
   mkdir -p /home/pi/TonyPi/ActionGroups/
   
   # Create symlink to actual location
   ln -s /home/pi/one/tonypi_pro/TonyPi/ActionGroups/*.d6a /home/pi/TonyPi/ActionGroups/
   ```

## Other Common Issues

### Robot Not Responding
- Make sure you've called `ctl.enable_recv()` before reading sensors
- Check that the serial connection is working: `/dev/ttyAMA0` should be accessible
- Verify servos are powered and connected

### Import Errors
- Make sure the HiwonderSDK is installed:
  ```bash
  cd /home/pi/TonyPi/HiwonderSDK
  sudo python3 setup.py install
  ```

### Camera Not Working
- Check camera permissions
- Verify `/boot/camera_setting.yaml` exists
- Try restarting the camera service

