# compare environment
一个简单的脚本，用于为VSCode Debug时提供环境变量。GPGPU-Sim原版代码中用的是source命令，然而VSCode中无法在按F5时自动在同一bash下执行，因此退而求其次，抓取脚本产生的新环境变量，然后保存在`new_vars.sh`文件中。
## 使用方法
```bash
# assume that you are in gpgpu-sim folder
cd cmpenv
./getenv.sh
```
这会生成一个`new_vars.sh`文件。

然后手动把`new_vars.sh`文件路径复制到`launch.json`的`envFile`字段中即可。

## 参考
https://stackoverflow.com/questions/58289147/visual-studio-code-debug-source-and-then-launch-on-same-shell