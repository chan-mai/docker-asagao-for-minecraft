<div align="center">
  <img src="doc/img/asagao_logo_face3.png" alt="header" title="asagao-for-minecraft header">
</div>


# はじめに
これは[yosipyさん](https://github.com/yosipy)が作成した[asagao-for-minecraft](https://github.com/yosipy/asagao-for-minecraft)をDockerへ移植し、正常に動作するよう一部動作を変更したものです。  
  

## asagao-for-minecraftとは

Minecraftを遊んでいるとき以外もサーバー代金が発生するのは無駄です。  
Discordから指定のメッセージを送信すると、ConoHaにMinecraft用のVM(バーチャルマシンサーバー)を構築、もしくは(データを保存の上)VMの破棄を行います。  
これにより、マインクラフトを遊んでいる時間のみサーバーが課金され、安く運用することができます。  
  
遊び終わった後にDiscordに`/close`と投稿すると、VMデータを退避(imageへ保存)しVMを破棄します。  
これによって、破棄した後は料金の発生を防ぐことができます。  
  
また遊びたいときはDiscordに`/open`と投稿すると、退避していたimageからVMを作成します(使い終わったimageは破棄します)。  
これによって、ConoHaの課金が始まりますがMinecraftサーバーでまた遊べるようになります。  
  
## why asagao(朝顔)?

朝顔は夏の朝に咲く花です。咲いたその日のうちにしぼんでしまいます(儚い)。  
  
asagao-for-minecraftもConoHaのVMを構築し、破棄します。  
  
一度しか咲かない朝顔と違い、asagao-for-minecraftは何度でも構築と破棄を繰り返します。  
  
~~作者が朝顔は何度も咲くと勘違いして名付けました。~~  
  
後、リポジトリ名を入力したときに「わかってねぇなあ、イケてるリポジトリ名って短くて簡潔なんだよ(超意訳)」ってGithubに煽られたので短い名前を付けました。  


# コマンド



## 初期設定

### DiscordBotアカウントの作成

簡単に説明します。詳しくは[Discord Botのアカウント初期設定を行う](https://codelabo.com/posts/20210307103912)をご覧ください。  
  
1. [DEVELOPER PORTAL](https://discord.com/developers/applications)にアクセスしてログインします。
1. 「New application」から好きなアプリケーション名を入力して「create」します。
1. 必要ならアイコンを設定しましょう。
1. 「settings」->「Bot」->「build-a-bot」->「Add Bot」をクリックします。「Yes」をクリック。
1. 「settings」->「Bot」->「build-a-bot」->「Add Bot」->「Token」->「Copy」からアクセストークンを取得します。
1. 「settings」->「OAuth2」->「OAuth2 URL Generator」->「SCOPES」の「bot」にチェックを入れます。認証URLが生成されるのでアクセスし、使いたいサーバーを選択して、「認証」します。
  
これでDiscordアプリから作ったBotアカウントを確認できると思います。  
  
### サーバ上での前準備
まず、利用するために、repoをローカルにcloneします。  
```bash
git clone https://github.com/chan-mai/docker-asagao-for-minecraft
```

### 環境変数に値を設定する
環境変数を記述するファイルをテンプレートから用意するため、下記のコマンドを実行します。  
```bash
cp .env.sample .env
```
お好きなエディタで`.env`ファイルを開き、下記項目を適切に設定します。  
  
「CONOHA_API_」から始まる環境変数は[ConoHaの管理画面](https://manage.conoha.jp/API/)から確認できるものです。  
**注意**現在、ConoHaでは、var3.0がデフォルトですが、非対応のため、コンパネ左下のバージョン切り替えからvar2.0を選択し、た上で表示された情報を使用してください。  
  
DISCORD_TOKENを設定するとConoHaAPIを使わないコマンドは動くようになります。  
  
CONOHA_API_VM_PLAN_FLAVOR_UUIDは使用するConoHaのプランのIDです。  
`/plan`とDiscordのminecraftチャンネルで投稿すると、ConoHaのプラン一覧を表示してくれます。「g-c3m2d100」は3Core, 2GB memory, 容量100GBのはず。  
  
VM_AND_IMAGE_NAMEはConoHaで作成するVMのネームタグ(instance_name_tag)とimageの名前に使用されます。「asagao-for-minecraft-{VM_AND_IMAGE_NAME}」となります(例:VM_AND_IMAGE_NAME=testとすると、VMのネームタグとimageの名前は「asagao-for-minecraft-test」となります)。  
デフォルトのVMのネームタグとimageの名前は「asagao-for-minecraft」です。  
  
ADMIN_USER_IDは管理してる人のユーザーIDです。  
  
DISCORD_CHANNEL_NAMESはコマンドを実行できるDiscordチャンネル名をコンマ区切りで指定します。  
デフォルトは`minecraft, minecraft-test`が指定されてます。  
例えばこれに加えて`minecraft-dev`を追加したいのであれば、DISCORD_CHANNEL_NAMESに`minecraft, minecraft-test, minecraft-dev`と入力します。  

#### 必須の環境変数
|値|説明|
|---|---|
|DISCORD_TOKEN|前項で作成したDiscordBotのトークン|
|CONOHA_API_TENANT_ID|ConoHaAPIのテナントID|
|CONOHA_API_IDENTITY_SERVICE|ConoHaのIdentity Serviceエンドポイント|
|CONOHA_API_USER_NAME|ConoHaのAPIユーザー名|
|CONOHA_API_USER_PASSWORD|ConoHaのAPIユーザーパスワード|
|CONOHA_API_IMAGE_SERVICE|ConoHaのImage Serviceエンドポイント|
|CONOHA_API_COMPUTE_SERVICE|ConoHaのCompute Serviceのエンドポイント|
|CONOHA_API_NETWORK_SERVICE|ConoHaのNetwork Serviceのエンドポイント|
|CONOHA_API_VM_PLAN_FLAVOR_UUID|VPSで使用するプランのUUID(botの起動後、/planで確認可)|
|DISCORD_CHANNEL_NAMES|操作を許可するDiscordのチャンネル名(,区切りで複数記述可)|
|DISCORD_GUILD_IDS|操作を許可するDiscordサーバーのGuildID(,区切りで複数記述可)|
#### オプション環境変数
|値|説明|
|---|---|
|VM_AND_IMAGE_NAME|イメージの名称(サービスアカウント内で一意の文字列である必要があります)|
|ADMIN_USER_ID|管理者のDiscordユーザーID|
|HOUR_FOR_IMAGE_LEAVE_ALONE_LONG_TIME|イメージの警告通知を行う時間(0-23)|

## ConoHaでMinecraft用のVMを作成する

ConoHaでサーバー追加をクリックし、Minecraft用のVMを作成していきます。  
  
- サービス = Minecraft
- VPS割引きっぷ = 利用しない
- プラン = 1GB以上
- イメージタイプ = 好きな方(私はJava版)
- root パスワード = 必ず控えておいてください。マイクラの難易度を変更したり、サーバーの設定に必要です(万一忘れた場合は手動でイメージからVMを作り直してパスワードを再設定してください)。
- ネームタグ = asagao-for-minecraft もしくはVM_AND_IMAGE_NAMEを設定してるならasagao-for-minecraft-{VM_AND_IMAGE_NAME}
  
この設定でサーバー追加(VM作成)します。  

## 実際に使ってみましょう

上記の手順でVMを作成しているため、料金が発生している状態です。  
以下のコマンドで一度VMを閉じましょう。  
  
```
/close
```
  
無事成功すれば、サーバーリストから先ほど作成したVMが消えていることが確認できます。
その際に、保存イメージを確認するとVPSと同様のネームタグが付いたイメージが新たに生成されていることが確認できます。  
この状態では料金が発生しません。  
  
また、遊びたくなったら、以下のコマンドを実行します。  
  
```
/open
```
  
無事成功すれば、サーバーリストに新しくVMが生成され、保存されていたイメージはなくなっていることが管理画面から確認できると思います。  
  
VMを再作成している仕様上、毎回サーバーのipアドレスは変更してしまいます。Discordに表示されたものを使用してください。  
  
また、コマンドの一覧は以下のコマンドで確認できます。  

```
/help
```


# 注意事項

## ConoHa imageを90日以上放置しないでください
[ConoHaの仕様上、VPS作成および追加ディスク作成に利用されず、90日を経過したイメージは削除対象となるようです](https://support.conoha.jp/v/saveimages/)。なので`/close`してから90日間放置するとイメージを消される恐れがあります。1か月程度おきに`/open_and_close`を行うことをおすすめします。  
  
環境変数`HOUR_FOR_IMAGE_LEAVE_ALONE_LONG_TIME`に0～23までの数字を入力することによって、10日、20日、30日以降のタイミングで再起動を促す機能を作成してます。
0～23の数字は通知する時間です。  

# Tokenなどの情報管理に気を付けてください

TokenやパスワードをGitで管理しないでください。  
  
間違えて公開リポジトリにアップロードする危険があります。  
  
他の人に見られないように管理してください。  


# 問題発生時

API通信がうまくいかなかったときなど、エラーを出して処理が中断、もしくはスクリプトの実行を終了したりする場合があります。
  
エラーが出た場合はコンテナを再起動してください。  
restartのみでうまくいくこともありますが、ConoHaの管理画面から手を加えなければいけない時もあります。  
  
imageとVMの両方が存在している場合、作成しかけている方を手動で削除してください。  
imageとVMの両方が存在している場合、本スクリプトでは操作できません。削除する際は可能であればバックアップを取ることをおすすめします。  
ちなみにimageとVMそれぞれにおいて、同じ名前(もしくはネームタグ)は1つまでです。  


# 細かい仕様

imageやVMを削除する前にその両方が有効な状態かチェックしています。これにより、意図しない挙動によってデータが消えるリスクを軽減しています。

imageの判別にはimageの名前(name)、VMの判別にはVMのネームタグ(instance_name_tag)を使用しています。同じものを複数作成しないでください。

asagao-for-minecraftは[discord.py](https://github.com/Rapptz/discord.py)とConoHaAPIを用いています。アイコンの作成には[Textcraft](https://textcraft.net/)を使用しています。
