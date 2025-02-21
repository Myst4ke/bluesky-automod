# bluesky-automod

###  Configuration des identifiants avec un fichier `.env`

#### 🟢 Création du fichier `.env`
Dans le **répertoire de votre projet**, créez un fichier `.env` contenant vos identifiants **Bluesky** :

```
BSKY_HANDLE=votre_identifiant.bsky.social
BSKY_APP_PASSWORD=abcd-efgh-ijkl-mnop
```

🔹 **Remarque :** Utilisez un **App Password** généré via [les paramètres de Bluesky](https://bsky.app/settings/app-passwords), et non votre mot de passe principal.


---



###  Installation de ChromeDriver pour Selenium

#### 🟢 1. Vérifier la version de Google Chrome installée  
Avant d'installer ChromeDriver, il faut connaître la version de Google Chrome utilisée.

##### 🔹 Sur Linux / WSL
```bash
google-chrome --version
```

##### 🔹 Sur macOS
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version
```

##### 🔹 Sur Windows (PowerShell)
```powershell
Get-ItemProperty 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome' | Select-Object DisplayVersion
```

---

#### 🟢 2. Télécharger la version correspondante de ChromeDriver  
🔗 **Rendez-vous sur** [ChromeDriver Downloads](https://sites.google.com/chromium.org/driver/) et téléchargez la version correspondant à votre Chrome.

---

#### 🟢 3. Installer ChromeDriver  

##### 🔹 Sur Linux / WSL
```bash
unzip chromedriver-linux64.zip
sudo mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
sudo chmod +x /usr/local/bin/chromedriver
```
💡 Vérifier l'installation :
```bash
chromedriver --version
```

##### 🔹 Sur macOS
```bash
unzip chromedriver-mac-x64.zip
sudo mv chromedriver /usr/local/bin/chromedriver
sudo chmod +x /usr/local/bin/chromedriver
```

##### 🔹 Sur Windows
1. **Décompressez** `chromedriver-win64.zip`.
2. **Déplacez `chromedriver.exe`** dans `C:\Windows\System32\` ou ajoutez son chemin aux **variables d'environnement**.
3. **Vérifiez l'installation** :
```powershell
chromedriver --version
```
