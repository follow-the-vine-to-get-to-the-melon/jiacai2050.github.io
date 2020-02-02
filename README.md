## 个人博客 | 技术 · 杂谈

> https://liujiacai.net/

- 总结与回顾
- 交流与反思

### 与我交流

- Email: `base64 -d <<< aGVsbG9AbGl1amlhY2FpLm5ldAo=`
- Telegram 群组：https://t.me/clojurists
- GPG key ID: `D3026E5C08A0BAB4`
  - Fingerprint: `6F734AE4297C7F62B6054F91D3026E5C08A0BAB4`
  - `curl https://keybase.io/liujiacai/pgp_keys.asc | gpg --import`

## 部署

- Node
- Hexo 3 + Maupassant

参考步骤：

### Hexo
```
# 需要确保 node 版本为 6.10.3/12.13.0
npm install hexo-cli -g
```

### 下载主题模版
```
git clone https://github.com/tufu9441/maupassant-hexo.git themes/maupassant
cp maupassant_config.yml themes/maupassant/_config.yml
# 之后为了全局显示 toc，需要修改 themes/maupassant/layout/post.pug 的
# if page.toc 为 if page.toc || 1

# 解决 ../src/sass_context_wrapper.h:8:10: fatal error: 'sass/context.h' file not found
brew install libsass

npm install

# 如果安装了 libsass 还是报头文件的错，直接下载 sass binary 文件
SASS_BINARY_SITE=https://npm.taobao.org/mirrors/node-sass/ npm install node-sass
rm -rf node_modules
npm install
```
参考：http://www.luckyzz.com/hexo/hexo-install-error/
