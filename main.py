import time
import os
import json
import traceback
from pystyle import *

SETTINGS_PATH = "settings.json"

if not os.path.exists("logs"):
    os.makedirs("logs")


def load_settings():
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as settings_file:
                return json.load(settings_file)
        except Exception:
            return {"quality": "high"}
    return {"quality": "high"}


def save_settings(quality):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as settings_file:
        json.dump({"quality": quality}, settings_file, ensure_ascii=False)


settings = load_settings()
DefaultQuality = settings.get("quality", "high")

def log_error(error_msg, exception=None):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {error_msg}"
    if exception:
        log_entry += f"\n{traceback.format_exc()}"
    print(Colors.red + log_entry + Colors.reset)
    with open("logs/errors.log", "a", encoding="utf-8") as log_file:
        log_file.write(log_entry + "\n" + "="*50 + "\n")

System.Clear()
System.Title("🌸 SakuraDL - Anime Downloader")
System.Init()
banner = r"""
   ███████╗ █████╗ ██╗  ██╗██╗   ██╗██████╗  █████╗ ██████╗ ██╗
   ██╔════╝██╔══██╗██║ ██╔╝██║   ██║██╔══██╗██╔══██╗██╔══██╗██║
   ███████╗███████║█████╔╝ ██║   ██║██████╔╝███████║██║  ██║██║
   ╚════██║██╔══██║██╔═██╗ ██║   ██║██╔══██╗██╔══██║██║  ██║██║
   ███████║██║  ██║██║  ██╗╚██████╔╝██║  ██║██║  ██║██████╔╝███████╗
   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝
                   🌸 SAKURA-DL 🌸
                🌸 YOUSSEF & SHROUK 🌸
"""

menu = """
╔══════════════════════════════════════════════╗
║                 MAIN MENU                    ║
╠══════════════════════════════════════════════╣
║  [1] Download Anime                          ║
║  [2] Settings                                ║
║  [3] About                                   ║
║  [0] Exit                                    ║
╚══════════════════════════════════════════════╝
"""

System.Clear()
Write.Print(
    Center.Center(banner),
    Colors.purple_to_blue,
    interval=0.002
)
time.sleep(2)
System.Clear()
print(Colorate.Vertical(Colors.blue_to_purple, Center.Center(menu)))

choice = input(Colors.cyan + "➜ Select Option: " + Colors.reset)
print(Colorate.Horizontal(Colors.green_to_cyan, f"\nSelected: {choice}"))

try:
    if choice == "1":
        from libs.anime_handler import handler
        from libs.downloader import media_downloader

        System.Clear()
        print(Colorate.Vertical(
            Colors.cyan_to_blue,
            Center.Center("""
╔════════════════════════════════════════╗
║            ANIME DOWNLOADER            ║
╚════════════════════════════════════════╝
        """)
        ))

        anime_url = input(Colors.yellow + "🔗 Enter Anime URL: " + Colors.reset).strip()

        if not anime_url:
            print(Colors.red + "❌ No URL provided!" + Colors.reset)
            time.sleep(2)
        else:
            try:
                print(Colors.cyan + "⏳ Loading anime info..." + Colors.reset)
                anime = handler(anime_url)
                anime_info = anime.load()
            except:
                pass
            System.Clear()
            print(Colors.green + f"✓ Title: {anime_info['title']}" + Colors.reset)
            print(Colors.cyan + f"📊 Episodes: {anime_info['episodes_count']}" + Colors.reset)
            print(Colors.cyan + f"⭐ Rating: {anime_info['rating']}" + Colors.reset)
            print()
            episode_menu = """
╔════════════════════════════════════════╗
║        EPISODE SELECTION MODE          ║
╠════════════════════════════════════════╣
║  [1] Single Episode                    ║
║  [2] Multiple Episodes (Range)         ║
║  [3] Batch Download (Auto Split)       ║
║  [4] Download All Episodes             ║
╚════════════════════════════════════════╝
            """
            print(Colorate.Vertical(Colors.blue_to_purple, Center.Center(episode_menu)))
            ep_choice = input(Colors.yellow + "➜ Select Mode (1-4): " + Colors.reset).strip()
            episodes_to_download = []

            if ep_choice == "1":
                ep_num = input(Colors.yellow + "Enter Episode Number: " + Colors.reset).strip()
                try:
                    ep_idx = int(ep_num) - 1
                    if 0 <= ep_idx < len(anime_info['episodes']):
                        episodes_to_download = [anime_info['episodes'][ep_idx]]
                    else:
                        print(Colors.red + "❌ Invalid episode number!" + Colors.reset)
                except ValueError:
                    print(Colors.red + "❌ Invalid input!" + Colors.reset)

            elif ep_choice == "2":
                start = input(Colors.yellow + "Start Episode: " + Colors.reset).strip()
                end = input(Colors.yellow + "End Episode: " + Colors.reset).strip()
                try:
                    start_idx = int(start) - 1
                    end_idx = int(end)
                    if 0 <= start_idx < len(anime_info['episodes']) and end_idx <= len(anime_info['episodes']):
                        episodes_to_download = anime_info['episodes'][start_idx:end_idx]
                    else:
                        print(Colors.red + "❌ Invalid range!" + Colors.reset)
                except ValueError:
                    print(Colors.red + "❌ Invalid input!" + Colors.reset)

            elif ep_choice == "3":
                batch_input = input(Colors.yellow + "Enter episode numbers (comma-separated, e.g., 2,5,9): " + Colors.reset).strip()
                try:
                    episode_numbers = [int(x.strip()) for x in batch_input.split(',')]
                    episodes_to_download = []
                    for ep_num in episode_numbers:
                        if 1 <= ep_num <= len(anime_info['episodes']):
                            episodes_to_download.append(anime_info['episodes'][ep_num - 1])
                        else:
                            print(Colors.red + f"❌ Episode {ep_num} doesn't exist!" + Colors.reset)
                    if not episodes_to_download:
                        print(Colors.red + "❌ No valid episodes selected!" + Colors.reset)
                except ValueError:
                    print(Colors.red + "❌ Invalid format! Use comma-separated numbers (e.g., 2,5,9)" + Colors.reset)

            elif ep_choice == "4":
                confirm = input(Colors.yellow + f"Download all {len(anime_info['episodes'])} episodes? (y/n): " + Colors.reset).strip().lower()
                if confirm == 'y':
                    episodes_to_download = anime_info['episodes']

            if episodes_to_download:
                System.Clear()
                print(Colors.green + "🚀 Starting Download..." + Colors.reset)
                print(Colors.cyan + f"Total Episodes: {len(episodes_to_download)}" + Colors.reset)
                time.sleep(1)

                for idx, episode in enumerate(episodes_to_download, 1):
                    print()
                    print(Colors.blue + f"[{idx}/{len(episodes_to_download)}] Downloading: {episode['name']}" + Colors.reset)
                    try:
                        download_url = anime.episode_loader(episode, quality_preference=DefaultQuality)
                        if download_url:
                            downloader = media_downloader()
                            result = downloader.download(
                                download_url,
                                anime_name=anime_info['title'],
                                output_title=f"{episode['number']} - {episode['name']}.%(ext)s"
                            )
                            if result["success"]:
                                print(Colors.green + f"✓ Episode {episode['number']} Downloaded!" + Colors.reset)
                            else:
                                print(Colors.red + f"❌ Download failed: {result['error']}" + Colors.reset)
                                log_error(f"Download failed for {episode['number']}: {result['error']}")
                        else:
                            print(Colors.red + "❌ Could not get download URL!" + Colors.reset)
                    except Exception as e:
                        log_error(f"Error loading episode {episode['number']}: {str(e)}", e)

                print()
                print(Colors.green + "✓ Download Complete!" + Colors.reset)
                time.sleep(2)
            else:
                print(Colors.red + "❌ No episodes selected!" + Colors.reset)
                time.sleep(2)

    elif choice == "2":
        System.Clear()
        settings_header = """
╔════════════════════════════════════════╗
║               SETTINGS                 ║
╚════════════════════════════════════════╝
        """
        print(Colorate.Vertical(Colors.cyan_to_blue, Center.Center(settings_header)))
        print(Colors.yellow + f"Current Quality: {DefaultQuality.upper()}" + Colors.reset)
        print()
        settings_menu = """
╔════════════════════════════════════════╗
║        VIDEO QUALITY SETTINGS          ║
╠════════════════════════════════════════╣
║  [1] High Quality (1080p)              ║
║  [2] Mid Quality (720p)                ║
║  [3] Low Quality (480p)                ║
║  [0] Back to Main Menu                 ║
╚════════════════════════════════════════╝
        """
        print(Colorate.Vertical(Colors.blue_to_purple, Center.Center(settings_menu)))
        settings_choice = input(Colors.yellow + "➜ Select Quality: " + Colors.reset).strip()

        if settings_choice == "1":
            DefaultQuality = "high"
            save_settings(DefaultQuality)
            print(Colors.green + "✓ Quality set to HIGH (1080p)" + Colors.reset)
        elif settings_choice == "2":
            DefaultQuality = "mid"
            save_settings(DefaultQuality)
            print(Colors.green + "✓ Quality set to MID (720p)" + Colors.reset)
        elif settings_choice == "3":
            DefaultQuality = "low"
            save_settings(DefaultQuality)
            print(Colors.green + "✓ Quality set to LOW (480p)" + Colors.reset)
        elif settings_choice == "0":
            pass
        else:
            print(Colors.red + "❌ Invalid choice!" + Colors.reset)
        time.sleep(2)

    elif choice == "3":
        System.Clear()
        about_header = """
╔════════════════════════════════════════╗
║               ABOUT                    ║
╚════════════════════════════════════════╝
        """
        print(Colorate.Vertical(Colors.cyan_to_blue, Center.Center(about_header)))
        about_text = f"""
{Colors.green}🌸 SAKURA-DL v1.0{Colors.green}
{Colors.cyan}An Anime Downloader Application{Colors.cyan}

{Colors.cyan}✓ Developer:{Colors.yellow} Youssef & Shrouk
{Colors.cyan}✓ License:{Colors.green} MIT

{Colors.yellow}Features:{Colors.cyan}
  • Download anime episodes in multiple qualities
  • Single, range, batch, or full series download
  • Beautiful TUI with animated menus
  • Support for anime3rb.com
        """
        for line in about_text.split('\n'):
            if line.strip():
                print(line)
        print()
        time.sleep(5)

    elif choice == "0":
        System.Clear()
        exit_message = """
╔════════════════════════════════════════╗
║       Thank you for using SAKURA-DL    ║
║              Goodbye!!                 ║
╚════════════════════════════════════════╝
        """
        print(Colorate.Vertical(Colors.red_to_yellow, Center.Center(exit_message)))
        time.sleep(2)
        exit()

    else:
        print(Colors.red + "❌ Invalid choice!" + Colors.reset)
        time.sleep(2)

except Exception as e:
    log_error(f"Unexpected error in main menu: {str(e)}", e)
    print(Colors.red + "📝 Check 'logs/errors.log' for detailed error information" + Colors.reset)
    time.sleep(3)
