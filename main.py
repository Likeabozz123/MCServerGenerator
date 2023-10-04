import requests
from bs4 import BeautifulSoup
import logging
import os
import xmltodict

logging.basicConfig(filename="debug.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
log = logging.getLogger()
log.setLevel(logging.DEBUG)

print("MINECRAFT SERVER GENERATOR")

server_name = input("What would you like your server to be named?\n")
os.mkdir(f"./{server_name}")
path = f"./{server_name}"
log.debug(f"Created a new directory for {server_name}")
ram_allocation = input("How much ram would you like to allocate? (in gbs)\n")
server_port = int(input("What would you like the server port to be? (default : 25565)\n") or "25565")
java_dir = input("Input a java directory (If you don't know what this is, just leave it blank)\n") or "java"

print("1. Vanilla")  # https://mcversions.net/ (Parsing the link)
print("2. Paper")  # https://papermc.io/api/docs/swagger-ui/index.html?configUrl=/api/openapi/swagger-config#/
print("3. Forge")  # Manual parsing
print("4. Fabric")  # Manual parsing

match input("Select the type of server you would like\n"):
    case "1":
        print("You have selected Vanilla")
        log.debug("Choosing the Vanilla server set")
        mc_version = input("Type the version you wish to download\n")
        log.debug(f"Minecraft Version : {mc_version}")
        print("Downloading...")
        url = f"https://mcversions.net/download/{mc_version}"
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')
        log.debug("Parsing 'https://mcversions.net' for the download link ")
        for link in soup.find_all('a'):
            if "server.jar" in link.get('href'):
                server_jar = requests.get(link.get('href'), allow_redirects=True)
                open(f"{path}/minecraft-{mc_version}.jar", 'wb').write(server_jar.content)
        print(f"Successfully downloaded minecraft-{mc_version}.jar")
        log.debug(f"Successfully downloaded minecraft-{mc_version}.jar")
        file = f"minecraft-{mc_version}.jar"
    case "2":
        print("You have selected Paper")
        log.debug("Choosing the Paper server set")
        mc_version = input("Type the version you wish to download\n")
        log.debug(f"Minecraft Version : {mc_version}")
        print("Downloading...")
        builds = requests.get(f"https://papermc.io/api/v2/projects/paper/versions/{mc_version}")
        latest_build = builds.json()['builds'][-1]
        build_info = requests.get(
            f"https://papermc.io/api/v2/projects/paper/versions/{mc_version}/builds/{latest_build}/")
        file_name = build_info.json()['downloads']['application']['name']
        server_jar = requests.get(
            f"https://papermc.io/api/v2/projects/paper/versions/{mc_version}/builds/{latest_build}/downloads/{file_name}")
        open(f"{path}/paper-{mc_version}-{latest_build}.jar", 'wb').write(server_jar.content)
        print(f"Successfully downloaded paper-{mc_version}-{latest_build}.jar")
        log.debug(f"Successfully downloaded paper-{mc_version}-{latest_build}.jar")
        file = f"paper-{mc_version}-{latest_build}.jar"
    case "3":
        print("You have selected Forge")
        log.debug("Choosing the Forge server set")
        mc_version = input("Type the version you wish to download\n")
        log.debug(f"Minecraft Version : {mc_version}")
        url = "https://files.minecraftforge.net/net/minecraftforge/forge/index_{version}.html".format(
            version=mc_version)
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')
        log.debug("Parsing 'https://files.minecraftforge.net/net/minecraftforge/forge/' for the download link ")
        links = []
        for link in soup.find_all('a'):
            if "Installer" in str(link.get('title')):
                links.append(str(link.get('href'))[48:])
        for i in range(len(links)):
            print(f"{i + 1}. {links[i].split('/')[-2]}")
        forge_version = input("Select the version you want for your forge server\n")
        print("Downloading...")
        forge_build = links[int(forge_version) - 1].split('/')[-2]
        installer_jar = requests.get(links[int(forge_version) - 1], allow_redirects=True)
        installer_file = f"forge-{forge_build}-installer.jar"
        open(f"{path}/{installer_file}", 'wb').write(installer_jar.content)
        print(f"Successfully downloaded {installer_file}")
        log.debug(f"Successfully downloaded {installer_file}")
        log.debug("Running the forge file to download server files")
        os.system(f'java -jar "{path}/{installer_file}" --installServer "{path}"')
        file = f"forge-{forge_build}.jar"
    case "4":
        print("You have selected Fabric")
        log.debug("Choosing the Fabric server set")
        mc_version = input("Type the version you wish to download\n")
        log.debug(f"Minecraft Version : {mc_version}")
        maven_repository = "https://maven.fabricmc.net/net/fabricmc/fabric-installer/"
        metadata_xml = requests.get("https://maven.fabricmc.net/net/fabricmc/fabric-installer/maven-metadata.xml")
        metadata = xmltodict.parse(metadata_xml.content)
        release_version = metadata['metadata']['versioning']['release']
        installer_jar = requests.get(
            f"https://maven.fabricmc.net/net/fabricmc/fabric-installer/{release_version}/fabric-installer-{release_version}.jar",
            allow_redirects=True)
        installer_file = f"fabric-installer-{release_version}.jar"
        open(f"{path}/{installer_file}", 'wb').write(installer_jar.content)
        os.system(f"cd {path}")
        os.system(
            f'java -jar "{path}/{installer_file}" server -mcversion {mc_version} -dir "{path}" -downloadMinecraft')
        file = "fabric-server-launch.jar"

batch_script = "@echo off\n" \
               f'title Minecraft Server Console [{server_name}]\n' \
               "color 07\n" \
               "cls\n" \
               f'"{java_dir}" -Xms{int(ram_allocation)}G -Xmx{int(ram_allocation)}G -XX:+UseG1GC ' \
               f'-XX:+ParallelRefProcEnabled ' \
               f"-XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch " \
               f"-XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 " \
               f"-XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 " \
               f"-XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 " \
               f"-XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -Dusing.aikars.flags=https://mcflags.emc.gs " \
               f"-Daikars.new.flags=true -jar {file} nogui\n" \
               "pause"
open(f"{path}/run.bat", 'wt').write(batch_script)
log.debug("Created run.bat file")
eula = "eula=true"
open(f"{path}/eula.txt", 'wt').write(eula)
log.debug("Created eula.txt file")
server_properties = f"server-port={server_port}\n" \
                    "difficulty=normal"
open(f"{path}/server.properties", 'wt').write(server_properties)
log.debug("Created server.properties file")
