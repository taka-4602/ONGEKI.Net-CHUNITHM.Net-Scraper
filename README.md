# ONGEKI.Net-CHUNITHM.Net-Scraper 
オンゲキ NET と チュウニズム NETから情報を取得するAPIラッパー、マイマイの予定はありません  
## インストール  
音擊  
```
pip install ongeki-scraper
```  
チュウニズム  
```
pip install chunithm-scraper
```
必須:bs4  
## Webでできることしかできません 
あたりまえですが、無料アカウントでプレミアムアカウントの機能使ったりは無理です  
というかそもそもjson受け取れるようなAPIはなかったので100% Webスクレイピングです 
## まずは音撃から  
#### example_ongeki.py
```py
from ongeki_screper import ONGEKI

ongeki=ONGEKI("SEGA ID","パスワード")#SEGA IDとパスワードでログイン
print(ongeki.token,ongeki.user_id)#セッションの維持に必要なトークンとユーザーID !!ユーザーIDという名前なだけでランダムに変わるクッキーです!!
print(ongeki.name)#プレイヤー名
print(ongeki.plate)#プレートの文字
print(ongeki.rating,ongeki.raiting_max)#レート
print(ongeki.battle_point)#バトルポイント
print(ongeki.money,ongeki.money_total)#マニー
print(ongeki.leveling,ongeki.leveling_reincarnation)#レベルと転生回数
print(ongeki.icon)#アイコン画像
print(ongeki.character)#キャラクター画像
print(ongeki.course)#利用券
ongeki=ONGEKI(token=ongeki.token,user_id=ongeki.user_id)#トークンとユーザーIDでログインをスキップ
all_music=ongeki.get_all_music()#難易度別で全曲を取得
rating_music=ongeki.check_rating_music()#レーティング対象曲をすべて取得
print(rating_music.rating_new)#新曲枠
print(rating_music.rating_best)#ベスト枠
print(rating_music.rating_recent)#リーセント枠
print(rating_music.rating_candidate)#候補枠
check_rating_music=rating_music.rating_best[0]#ベスト枠はリストなので1番上を取得
score_detail=ongeki.music_score_details(check_rating_music["idx"])#idxが曲の詳細を取得するためのトークンみたいなもの
print(score_detail.music_title)#タイトル
print(score_detail.music_img)#ジャケットの画像
print(score_detail.music_artist)#アーティスト
print(score_detail.music_genre)#ジャンル
print(score_detail.music_enemy)#敵の情報
print(score_detail.MASTER_battle_score)#バトルスコア
print(score_detail.MASTER_technical_score)#テクニカルスコア
print(score_detail.MASTER_icon_technical_rank)#テクニカルランク
print(score_detail.MASTER_over_damage)#オーバダメージ
print(score_detail.MASTER_last_played)#最終プレイ日
history=ongeki.get_history()#プレイ履歴を取得
last_played=history[0]#プレイ履歴の1番上
playlog_score_detail=ongeki.playlog_score_details(last_played["idx"])#idxを使ってプレイ履歴の詳細を取得
print(playlog_score_detail.music_title)#タイトル
print(playlog_score_detail.music_img)#ジャケット画像
print(playlog_score_detail.music_difficulty)#難易度
print(playlog_score_detail.music_battle_score)#バトルスコア
print(playlog_score_detail.music_technical_score)#テクニカルスコア
print(playlog_score_detail.music_over_damage)#オーバーダメージ
print(playlog_score_detail.max_combo)#コンボ数
print(playlog_score_detail.critical_break)#クリティカルブレイク
print(playlog_score_detail.ongeki_break)#ブレイク
print(playlog_score_detail.hit)#ヒット
print(playlog_score_detail.miss)#ミス
print(playlog_score_detail.damage)#ダメージ
print(playlog_score_detail.tap)#タップ
print(playlog_score_detail.hold)#ホールド
print(playlog_score_detail.side_tap)#サイドタップ
print(playlog_score_detail.side_hold)#サイドホールド
```  
#コメントに書いてある通り...  
### それ以外の返り値
##### レーティング対象曲 / プレイ履歴  
```
{'title': 'きゅうくらりん', 'level': '14', 'difficulty': 'Master', 'technical_score': '994,198', 'technical_score_int': 994198, 'idx': 'tD6VKJAiSJqbOH2pSJJjTON434ODt50u7C9krAwAFPPhowOm3tEW0atNrTgLAIWzQ7YaMdJxKOGOxp3urrR%2BtA%3D%3D'}
```
dictの中に簡易的な説明が入ってるので単にテクニカルスコアだけ知りたい場合、スコアの詳細を取得しなくてもだいじょうぶ  
##### 全曲
プレイ済み
```
'Cutter':{'idx': 'hEr/DTD/cn70Wlvr%2BQXFdJoAZQxOqZI6ohty6tyx8O4AhuqhZKYBKf5H8/prgd3Zh72wyfQG6oVFQqNuErzKcA%3D%3D', 'battle_score': '302.01%', 'over_damage': '9,752,464', 'technical_score': '1,003,145'}
```  
未プレイ  
```
'Recollect Lines':{'idx': 'G4LE%2BayGWh88q9ziJBDOyQuZRl088qgKmAFN0hAWbd5C/UEBmGISVIASZyJJpCqSovY7EODj6EjGbMUeal/zTw%3D%3D', 'battle_score': None, 'over_damage': None, 'technical_score': None}
```
dict in dictになっているため、```all_music["曲名"]``` でidxやスコアを確認できる  
#### スコア詳細
```
SCORE_DETAILS(MASTER_level='13+', MASTER_last_played='2024/11/11 20:28', MASTER_play_count='31', MASTER_over_damage='298.52%', MASTER_battle_score='9,730,844', MASTER_technical_score='998,888', MASTER_icon_battle_rank='https://ongeki-net.com/ongeki-mobile/img/music_icon_br_great.png?ver=1.45.0', MASTER_icon_technical_rank='https://ongeki-net.com/ongeki-mobile/img/music_icon_tr_ss.png?ver=1.45.0', MASTER_icon_bell='https://ongeki-net.com/ongeki-mobile/img/music_icon_fb.png', MASTER_icon_combo='https://ongeki-net.com/ongeki-mobile/img/music_icon_back.png', EXPERT_level='12', EXPERT_last_played='2024/09/26 19:03', EXPERT_play_count='17', EXPERT_over_damage='303.69%', EXPERT_battle_score='9,396,988', EXPERT_technical_score='1,007,995', EXPERT_icon_battle_rank='https://ongeki-net.com/ongeki-mobile/img/music_icon_br_excellent.png?ver=1.45.0', EXPERT_icon_technical_rank='https://ongeki-net.com/ongeki-mobile/img/music_icon_tr_sssplus.png?ver=1.45.0', EXPERT_icon_bell='https://ongeki-net.com/ongeki-mobile/img/music_icon_fb.png', EXPERT_icon_combo='https://ongeki-net.com/ongeki-mobile/img/music_icon_fc.png?ver=1.45.0', LUNATIC_level=None, LUNATIC_last_played=None, LUNATIC_play_count=None, LUNATIC_over_damage=None, LUNATIC_battle_score=None, LUNATIC_technical_score=None, LUNATIC_icon_battle_rank=None, LUNATIC_icon_technical_rank=None, LUNATIC_icon_bell=None, LUNATIC_icon_combo=None, music_img='https://ongeki-net.com/ongeki-mobile/img/music/c159c9bee6a1fb73.png', music_title='Cyaegha', music_genre='VARIETY', music_artist='USAO「Arcaea」', music_enemy='光 Lv.35')
```  
レベル別になってるので長い、プレイしていないレベルは```None```
#### プレイ履歴のスコア詳細  
```
SCORE_DETAILS(played='2024/11/11 20:34', music_img='https://ongeki-net.com/ongeki-mobile/img/music/5ab5414aa44d6a03.png', music_title='Knight Rider', music_battle_score='9,282,581', music_over_damage='323.16％', music_technical_score='986,641', max_combo='731', critical_break='1,149', ongeki_break='128', hit='39', miss='4', bell='117/117', damage='4', music_difficulty='Master', tap='95%', hold='99%', flick='99%', side_tap='96%', side_hold='100%')
```
こっちはブレイク数やタップの詳細なども取得できる  


