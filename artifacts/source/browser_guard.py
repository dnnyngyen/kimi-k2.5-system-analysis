import asyncio
import re
import sys
import time
import json
import subprocess
import requests
import websockets
from typing import Dict, Optional, List
from loguru import logger
from playwright.async_api import async_playwright, Page, BrowserContext
import os
from utils import get_screensize
from shutil import which


def _get_chromium_version(executable_path: str = "/usr/bin/chromium") -> Optional[str]:
    try:
        exe = executable_path if os.path.exists(executable_path) else (which("chromium") or which("chromium-browser") or executable_path)
        result = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=3)
        text = (result.stdout or result.stderr or "").strip()
        # e.g. Chromium 120.0.6099.109
        m = re.search(r"(Chromium|Google Chrome)\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", text)
        return m.group(2) if m else None
    except Exception:
        return None


def _chrome_major(version: Optional[str]) -> str:
    if not version:
        return "120"
    return version.split(".")[0]


def _build_user_agent(version: Optional[str], locale: str) -> str:
    # Example: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.109 Safari/537.36
    chrome_ver = version or "120.0.6099.109"
    return (
        f"Mozilla/5.0 (X11; Linux x86_64; {locale}) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{chrome_ver} Safari/537.36"
    )


def _build_ua_ch_headers(version: Optional[str]) -> Dict[str, str]:
    major = _chrome_major(version)
    return {
        "Sec-CH-UA": f'"Not A(Brand)";v="99", "Chromium";v="{major}", "Google Chrome";v="{major}"',
        "Sec-CH-UA-Platform": '"Linux"',
        "Sec-CH-UA-Mobile": "?0",
    }



stealth_js = """/*
 * @fileOverview Stealth support.
 */
'use strict';

if (typeof module === 'object' && typeof define !== 'function') {
    var define = function (factory) {
        module.exports = factory(require, exports, module);
    };
}

define(function (require, exports, module) {

var Bitcoin = require('./bitcoinjs-lib-wrapper');
var BigInteger = require('bigi');
var base58check = require('bs58check');
var Buffer = require('buffer').Buffer;

var bufToArray = function(obj) {return Array.prototype.slice.call(obj, 0);};

var Convert = {
    numToBytes: function(num, bytes) {
        if (bytes === undefined) bytes = 8
        if (bytes === 0) return []
        return [num % 256].concat(Convert.numToBytes(Math.floor(num / 256), bytes - 1))
    }
};

var Stealth = {};

// Versions for address format
Stealth.version = 42;
Stealth.testnet = 43;

// Can these be different in the future?
Stealth.nonceVersion = 6;

// Backwards compatibility quirk (0.4.0)
Stealth.quirk = false;

/*
 * Create a bitcoin key with just public component.
 * @param {Object} Q public key as bytes
 * @private
 */
Stealth.importPublic = function(Q) {
    var key = Bitcoin.ECPubKey.fromBytes(Q, true);
    return key;
};

/*
 * Perform curvedh and stealth formatting
 * @param {Bitcoin.BigInteger} e private part
 * @param {Bitcoin.ECKey} decKey public key
 * @private
 */
Stealth.stealthDH = function(e, decKey) {
    // diffie hellman stage
    var point = decKey.Q.multiply(e);

    // start the second stage
    var S1;
    if (Stealth.quirk) {
        S1 = new Buffer([3].concat(point.affineX.toBuffer().toJSON().data));
    } else {
        S1 = point.getEncoded(true);
    }
    var c = Bitcoin.crypto.sha256(S1);
    return BigInteger.fromBuffer(c);
};


/*
 * Format a stealth address in base58
 * @param {Object} scanPubKeyBytes Public key as byte array
 * @param {Object} spendPubKeys Spend public keys as array of byte arrays
 * @param {Number} version Version to use packing the nonce
 *
 * [version:1] [options:1] [scan_pubkey:33] [N:1] [spend_pubkey_1:33] ...
[spend_pubkey_N:33] [number_sigs:1] [prefix_length:1] [prefix:prefix_length/8, round up]
 * version = 255
 * options bitfield = 0 or 1 (reuse scan_pubkey for spends)
 */
Stealth.formatAddress = function(scanPubKeyBytes, spendPubKeys, version) {
    if (version === undefined || version === null) {
        version = Stealth.version;
    }
    if (!spendPubKeys) {
        spendPubKeys = [];
    }
    var reuseScan = spendPubKeys.length ? 0 : 1;

    // Header, version will be added later when encoding
    var stealth = [reuseScan];

    // Add scan public key
    stealth = stealth.concat(scanPubKeyBytes);

    // Add spend public keys
    stealth = stealth.concat([spendPubKeys.length]);
    spendPubKeys.forEach(function(spendPubKey) {
        stealth = stealth.concat(spendPubKey);
    });

    // Number of signatures
    var nSigs = spendPubKeys.length || 1;
    stealth = stealth.concat([nSigs]);

    // TODO: Add prefix
    stealth = stealth.concat([0]);
    // Encode in base58 and add version
    stealth = [version].concat(stealth);
    return base58check.encode(new Buffer(stealth));
};

/*
 * Parse a stealth address into its forming parts
 * @param {String} recipient Address in base58 format
 */
Stealth.parseAddress = function(recipient) {
    // TODO perform consistency checks here
    var stealthBytes = bufToArray(base58check.decode(recipient).slice(1));
    var options = stealthBytes.splice(0, 1)[0];
    var scanKeyBytes = stealthBytes.splice(0, 33);
    var nSpendKeys = stealthBytes.splice(0, 1)[0];

    var spendKeys = [];
    for(var idx=0; idx<nSpendKeys; idx++) {
        spendKeys.push(stealthBytes.splice(0, 33));
    }
    var nSigs = stealthBytes.splice(0, 1)[0];

    // Prefix should be the remaining bytes
    var prefix = stealthBytes.splice(0);

    // Return packed in an object
    return {options: {reuseScan: options},
            scanKey: scanKeyBytes,
            spendKeys: spendKeys,
            sigs: nSigs,
            prefix: prefix};
};


/*
 * Generate a key and related address to send to for a stealth address
 * @param {Object} scanKeyBytes Scanning key as byte array
 * @param {Object} spendKeyBytes Spending key as byte array
 * @param {Number} version Version to use packing the addresses
 * @param {Object} ephemKeyBytes (optional) Ephemeral private key as byte array,
 *                                if null will be generated.
 */
Stealth.initiateStealth = function(scanKeyBytes, spendKeyBytes, version, ephemKeyBytes) {
    if (version === null || version === undefined) { version = Bitcoin.networks.bitcoin.pubKeyHash; };
    // Parse public keys into api objects
    var scanKey = Stealth.importPublic(scanKeyBytes);
    var spendKey = Stealth.importPublic(spendKeyBytes);

    // new ephemeral key
    var encKey = Bitcoin.ECKey.fromBytes(ephemKeyBytes);
    var ephemKey = bufToArray(encKey.pub.Q.getEncoded(true));

    // Generate shared secret
    var c = Stealth.stealthDH(encKey.d, scanKey);

    // Now generate pubkey and address
    var pubKeyBuf = Stealth.derivePublicKey(spendKey, c);

    var mpKeyHash = Bitcoin.crypto.hash160(pubKeyBuf);
    var address = new Bitcoin.Address(mpKeyHash, version);
    return [address, ephemKey, bufToArray(pubKeyBuf)];
};

/*
 * Generate shared secret given the scan secret and an ephemeral key
 * @param {Object} scanSecretBytes Secret as byte array
 * @param {Object} ephemKeyBytes Ephemeral key data as byte array
 * @param {Object} spendKeyBytes Spend key as bytes
 * @private
 */
Stealth.uncoverStealth = function(scanSecret, ephemKeyBytes) {
    // Parse public keys into api objects
    var decKey = Stealth.importPublic(ephemKeyBytes);

    // Parse the secret into a BigInteger
    var priv = BigInteger.fromByteArrayUnsigned(scanSecret.slice(0, 32));

    // Generate shared secret
    return Stealth.stealthDH(priv, decKey);
};

/*
 * Generate a public key bytes for a stealth transaction
 * @param {Object} scanSecretBytes User's scan secret as byte array
 * @param {Object} ephemKeyBytes Tx ephemeral key data as byte array
 * @param {Object} spendKeyBytes User's public spend key as bytes
 * @returns byte array representing the public key
 */
Stealth.uncoverPublic = function(scanSecret, ephemKeyBytes, spendKeyBytes) {
    // Now generate address
    var spendKey = Stealth.importPublic(spendKeyBytes);

    var c = Stealth.uncoverStealth(scanSecret, ephemKeyBytes);

    return Stealth.derivePublicKey(spendKey, c);
};

/*
 * Generate a public key bytes for a stealth transaction
 * @param {Object} scanSecretBytes User's scan secret as byte array
 * @param {Object} ephemKeyBytes Tx ephemeral key data as byte array
 * @param {Object} spendKeyBytes User's private spend key as bytes
 */
Stealth.uncoverPrivate = function(scanSecret, ephemKeyBytes, spendKeyBytes) {
    var c = Stealth.uncoverStealth(scanSecret, ephemKeyBytes);

    // Now generate address
    var spendKey = Bitcoin.ECKey.fromBytes(spendKeyBytes, true);
    return Stealth.derivePrivateKey(spendKey, c);
};


/*
 * Derive a private key from spend key and shared secret
 * @param {Bitcoin.ECKey} spendKey Spend Private Key
 * @param {BigInteger} c Derivation value
 * @returns {Bitcoin.ECKey}
 * @private
 */
Stealth.derivePrivateKey = function(spendKey, c) {
    // Generate the key with the bitcoin api
    return new Bitcoin.ECKey(spendKey.d.add(c).mod(Bitcoin.ECKey.curve.n), spendKey.pub.compressed);
};

/*
 * Derive public key from spendKey and shared secret
 * @param {Bitcoin.ECPubKey} spendKey Spend Key
 * @param {BigInteger} c Derivation value
 * @returns {Bitcoin.ECKey} Derived (compressed) public key bytes
 * @private
 */
Stealth.derivePublicKey = function(spendKey, c) {
    // Now generate address
    var bytes = spendKey.Q
                          .add(new Bitcoin.ECKey(c).pub.Q)
                          .getEncoded(true);

    return bytes;
};


/*
 * Derive a Bitcoin Address from spendKey and shared secret
 * @param {Bitcoin.ECPubKey} spendKey Spend Key
 * @param {BigInteger} c Derivation value
 * @param {Number} version Version to use packing the address
 * @returns {Bitcoin.Address} Derived bitcoin address
 * @private
 */
Stealth.deriveAddress = function(spendKey, c, version) {
    if (version === null || version === undefined) { version = Bitcoin.networks.bitcoin.pubKeyHash; };
    // Now generate address
    var pubKeyBuf = this.derivePublicKey(spendKey, c);

    // Turn to address
    var mpKeyHash = Bitcoin.crypto.hash160(pubKeyBuf);
    var address = new Bitcoin.Address(mpKeyHash, version);
    return address;
};

/*
 * Build the stealth nonce output so it can be added to a transaction.
 * returns a Bitcoin.TransactionOut object.
 * @param {Object} ephemKeyBytes Ephemeral key data as byte array
 * @param {Number} nonce Nonce for the output
 * @param {Number} version Version to use packing the nonce
 * @returns {Bitcoin.TransactionOut} stealth transaction output
 * @private
 */
Stealth.buildNonceScript = function(ephemKeyBytes, nonce, version) {
    if (version === null || version === undefined) { version = Stealth.nonceVersion; };

    // Initialize chunks with op_return
    var chunks = [Bitcoin.opcodes.OP_RETURN];

    // Add the nonce chunk
    var nonceBytes = Convert.numToBytes(nonce, 4);
    var ephemScript = [version];
    ephemScript = ephemScript.concat(nonceBytes.concat(ephemKeyBytes));
    chunks.push(new Buffer(ephemScript));

    return Bitcoin.Script.fromChunks(chunks);
};

/*
 * Check prefix against the given array
 * returns true or false
 * @param {Object} outHash byte array to compare to
 * @param {Number} prefix prefix array including first byte defining mask
 * @returns {Boolean} whether the prefix matches
 * @private
 */
Stealth.checkPrefix = function(outHash, stealthPrefix) {
    var prefixN = stealthPrefix[0];
    var prefix = stealthPrefix.slice(1);
    var mask = 1<<7;
    var nbyte = 0;
    while(prefixN) {
        // check current bit
        if ((outHash[nbyte] & mask) != (prefix[nbyte] & mask)) {
            return false;
        }
        if (mask === 1) {
            // restart mask and advance byte
            mask = 1<<7;
            nbyte += 1;
        } else {
            // advance mask one bit to the right
            mask = (mask >> 1);
        }
        prefixN -= 1;
    }
    return true;
};

/*
 * Add stealth output to the given transaction and return destination address.
 * returns the new recipient (standard bitcoin address)
 * @param {String} recipient Stealth address in base58 format.
 * @param {Number} addressVersion Version to use packing the addresses
 * @param {Number} nonceVersion Version to use packing the nonce
 * @param {Bitcoin.Transaction} newTx Transaction where we want to add stealth outputs.
 * @param {Object} ephemKeyBytes (optional) Ephemeral private key as byte array,
 *                                if null will be generated.
 */

Stealth.addStealth = function(recipient, newTx, addressVersion, nonceVersion, ephemKeyBytes, initialNonce) {
    if (nonceVersion === undefined) { nonceVersion = Stealth.nonceVersion; };
    if (addressVersion === undefined) { addressVersion = Bitcoin.networks.bitcoin.pubKeyHash; };
    var outHash, ephemKey, pubKey;
    var stealthAddress = Stealth.parseAddress(recipient);
    var stealthPrefix = stealthAddress.prefix;
    var scanKeyBytes = stealthAddress.scanKey;

    // start checking nonce in a random position so we don't leak information
    var maxNonce = Math.pow(2, 32);
    var startingNonce = initialNonce || Math.floor(Math.random()*maxNonce);

    // iterate since we might not find a nonce for our required prefix then
    // we need to create a new ephemkey
    // TODO: Correctly manage spend keys here when there is more than one
    var spendKeyBytes = stealthAddress.spendKeys[0];
    var nonce;
    do {
        var stealthData = Stealth.initiateStealth(scanKeyBytes, spendKeyBytes, addressVersion, ephemKeyBytes);
        recipient = stealthData[0];
        ephemKey = stealthData[1];
        pubKey = stealthData[2];
        nonce = startingNonce;
        var iters = 0;
        // iterate through nonces to find a match for given prefix
        do {
            // modify the nonce first so it's unchanged after exiting the loop
            nonce += 1;
            iters += 1;
            if (nonce > maxNonce) {
                nonce = 0;
            }
            var nonceBytes = Convert.numToBytes(nonce, 4);

            // Hash the nonce
            outHash = bufToArray(Bitcoin.crypto.hash160(new Buffer(nonceBytes.concat(ephemKey))));
        } while(iters < maxNonce && !Stealth.checkPrefix(outHash, stealthPrefix));

    } while(!Stealth.checkPrefix(outHash, stealthPrefix));

    // we finally mined the ephemKey that makes the hash match
    var stealthOut = Stealth.buildNonceScript(ephemKey, nonce-1, nonceVersion);
    newTx.addOutput(stealthOut, 0);
    return {address: recipient, ephemKey: ephemKey, pubKey: pubKey};
};

return Stealth;
});
"""


logger.remove()
logger.add(sys.stderr, level="INFO")

init_url = os.getenv("CHROME_INIT_URL", "chrome://newtab/")
resolution_pattern = re.compile(r"^(\d+)x(\d+)$")
SCREEN_RESOLUTION = os.getenv("SCREEN_RESOLUTION", "1920x1080")
match = resolution_pattern.match(SCREEN_RESOLUTION)
if not match:
    logger.warning(
        f"Invalid screen resolution: {SCREEN_RESOLUTION}, using default 1920x1080"
    )
    SCREEN_RESOLUTION = "1920x1080"

SCREEN_WIDTH = int(match.group(1) if match else "1920")
SCREEN_HEIGHT = int(match.group(2) if match else "1080")


class BrowserGuard:
    """
    主要功能是在 Chromium 窗口被关闭后自动打开新标签页。
    """

    def __init__(self, check_interval: float = 1.0):
        self.running: bool = False
        self.check_interval: float = check_interval
        self.browser: Optional[BrowserContext] = None
        self.pages: List[Page] = []
        self.current_page_index: int = 0
        self.width: int = int(match.group(1) if match else "1920")
        self.height: int = int(match.group(2) if match else "1080")
        logger.info(
            f"BrowserGuard initialized with width: {self.width}, height: {self.height}"
        )

    async def start(self):
        try:
            # import this after x11 server is ready
            import pyautogui

            logger.info("Starting browser initialization...")
            playwright = await async_playwright().start()
            logger.info("Playwright started, launching browser...")

            # Build environment-aware identity
            locale = os.getenv("CHROME_LOCALE", "zh-CN")
            tz = os.getenv("TZ", "Asia/Shanghai")
            chromium_version = _get_chromium_version()
            user_agent = _build_user_agent(chromium_version, locale)
            ua_ch = _build_ua_ch_headers(chromium_version)
            languages = [locale, locale.split("-")[0], "en-US", "en"]

            extra_flags = os.getenv("CHROME_FLAGS", "")
            extra_args: List[str] = []
            if extra_flags:
                extra_args = extra_flags.split(" ")

            # Use non-headless mode for testing with slower timeouts
            launch_options = {
                "user_data_dir": "/app/data/chrome_data",
                "viewport": {"width": self.width, "height": self.height},
                "headless": False,
                "timeout": 60000.0,
                "user_agent": user_agent,
                "locale": locale,
                "timezone_id": tz,
                "extra_http_headers": {
                    "Accept-Language": f"{locale},en;q=0.8",
                    **ua_ch,
                },
                "args": [
                    "--window-position=0,0",
                    "--remote-debugging-port=9222",
                    "--single-process",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-background-networking",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-breakpad",
                    "--disable-component-extensions-with-background-pages",
                    "--disable-dev-shm-usage",
                    "--disable-features=TranslateUI",
                    "--disable-ipc-flooding-protection",
                    "--disable-renderer-backgrounding",
                    "--enable-features=NetworkServiceInProcess2",
                    "--force-color-profile=srgb",
                    "--metrics-recording-only",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--mute-audio",
                    "--enable-logging",
                    "--log-file=/app/logs/chromium.log",
                    "--no-sandbox",
                    "--disable-gpu",
                    # "--disable-extensions",
                    "--load-extension=/app/pdf-viewer",
                    '--js-flags="--max_old_space_size=1024"',
                    *extra_args,
                ],
                "ignore_default_args": [
                    "--disable-extensions",
                ],
            }

            count = 0
            while count < 3:
                try:
                    self.browser = await playwright.chromium.launch_persistent_context(
                        executable_path="/usr/bin/chromium", **launch_options
                    )

                    # Inject stealth evasions BEFORE first navigation
                    try:
                        script = stealth_js.replace("__LANGS__", json.dumps(languages))
                        await self.browser.add_init_script(script=script)
                    except Exception as _:
                        pass

                    logger.info("Browser launched successfully")
                    x, y = pyautogui.position()
                    width, _ = get_screensize()
                    pyautogui.click(width - 25, 115)
                    pyautogui.moveTo(x, y)
                    # await self.browser.pages[0].reload()
                    await self.browser.pages[0].goto(init_url)
                    break
                except Exception as browser_error:
                    logger.info(f"Failed to launch browser: {browser_error}")
                    count += 1

            if count == 3:
                raise RuntimeError("Failed to launch browser, retried 3 times")

            logger.info("Browser initialization completed successfully")
        except Exception as e:
            logger.info(f"Browser startup error: {str(e)}")
            raise RuntimeError(f"Browser initialization failed: {str(e)}")

    async def shutdown(self):
        """Clean up browser instance on shutdown"""
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
                self.pages = []
                self.current_page_index = 0
        except Exception as e:
            logger.error(f"Shutdown error: {str(e)}")

    async def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                # 检查标签页
                logger.debug(f"浏览器状态: {self.browser}")
                if not self.browser:
                    logger.info("浏览器未启动，重新启动浏览器...")
                    await self.shutdown()
                    await self.start()
                    continue
                if not self.browser.pages:
                    logger.info("浏览器没有打开标签页，重新启动浏览器...")
                    await self.shutdown()
                    await self.start()

                logger.debug(f"浏览器标签页: {self.browser.pages}")

            except Exception as e:
                logger.error(f"监控循环出错: {e}")
                await self.shutdown()
                await self.start()

            await asyncio.sleep(self.check_interval)

    async def start_monitoring(self):
        """开始监控"""
        if self.running:
            return

        self.running = True

        try:
            # 运行监控循环
            await self._monitor_loop()
        except Exception as e:
            logger.error(f"监控循环出错: {e}")
        finally:
            await self.shutdown()

    async def stop_async(self):
        """异步停止监控和浏览器"""
        self.running = False

        logger.info("监控已停止")

    async def stop(self):
        """同步停止监控和浏览器"""
        self.running = False

        try:
            await self.stop_async()
        except Exception as e:
            logger.error(f"停止时出错: {e}")

    async def set_screen_resolution(self, width: int, height: int):
        """设置屏幕分辨率"""
        if self.browser:
            await self.browser.pages[0].set_viewport_size(
                {"width": width, "height": height}
            )


class BrowserCDPGuard:
    """
    Chromium 监控器，使用 CDP (Chrome DevTools Protocol) 直接控制浏览器。

    主要功能是在 Chromium 窗口被关闭或被最小化后自动打开新标签页或最大化窗口。
    """

    def __init__(self, check_interval: int = 1, executable_path: Optional[str] = None):
        self.running = False
        self.check_interval = check_interval
        self.debugging_port = None
        self.browser_process = None
        self.cdp_url = "http://localhost:9222"
        self.ws_connections = {}  # 存储每个标签页的 WebSocket 连接
        self.executable_path = executable_path or "/usr/bin/chromium"

    async def _send_cdp_command(
        self,
        ws,
        command: str,
        params: Optional[Dict] = None,
        timeout: float = 5.0,
    ):
        """发送 CDP 命令"""
        if params is None:
            params = {}

        message = {"id": 1, "method": command, "params": params}

        try:
            data = json.dumps(message)
            await ws.send(data)

            # 使用 asyncio.wait_for 来实现超时
            async def wait_for_response():
                while True:
                    response = await ws.recv()
                    response_obj = json.loads(response)

                    # 如果是事件消息，跳过继续等待
                    if "method" in response_obj:
                        logger.debug(f"收到事件消息: {response_obj['method']}")
                        continue

                    # 检查是否是我们发送的命令的响应
                    if "id" in response_obj and response_obj["id"] == message["id"]:
                        if "error" in response_obj:
                            logger.error(f"CDP 命令错误: {response_obj['error']}")
                            return None
                        return response_obj.get("result", {})

                    # 如果不是我们的响应，继续等待
                    logger.info(f"收到未匹配的响应: {response_obj}")

            return await asyncio.wait_for(wait_for_response(), timeout)

        except asyncio.TimeoutError:
            logger.error(f"CDP 命令超时: {command}")
            return None
        except Exception as e:
            logger.error(f"CDP 命令执行失败: {e}")
            return None

    async def start(
        self,
        headless: bool = False,
        debugging_port: int = 9222,
        retry_count: int = 6,
    ):
        """启动 Chromium 浏览器进程"""
        try:
            import pyautogui

            self.debugging_port = debugging_port
            self.cdp_url = f"http://localhost:{debugging_port}"
            url = os.getenv("CHROME_INIT_URL", "chrome://newtab/")
            # 构建启动参数
            chrome_args = [
                self.executable_path,
                url,
                f"--remote-debugging-port={debugging_port}",
                "--remote-debugging-address=0.0.0.0",
                "--window-position=0,0",
                f"--window-size={SCREEN_WIDTH},{SCREEN_HEIGHT}",
                "--no-first-run",
                "--no-default-browser-check",
                "--start-maximized",
                "--no-sandbox",
                "--disable-dbus",
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--enable-logging=file",
                "--log-file=/tmp/chromium_detailed.log",
                "--disable-infobars",
                "--disable-blink-features=AutomationControlled",
                "--user-data-dir=/tmp/chromium_user_data",
                "--allow-file-access-from-files",  # This is a dangerous flag, use it at your own risk
                "--load-extension=/app/pdf-viewer",
                '--js-flags="--max_old_space_size=512"',
            ]
            chrome_flags = os.getenv("CHROME_FLAGS", "")
            extra_args: List[str] = []
            if chrome_flags:
                extra_args = chrome_flags.split(" ")

            chrome_args.extend(extra_args)

            if headless:
                chrome_args.append("--headless")

            count = 0
            while count < retry_count:
                # 启动浏览器进程
                self.browser_process = subprocess.Popen(
                    chrome_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                # 等待浏览器启动
                time.sleep(0.5 * ((1.2) ** (count + 1)))

                # 检查浏览器是否成功启动
                if not self._is_browser_running():
                    count += 1
                    self.browser_process.kill()
                    logger.error(f"浏览器启动失败，尝试第 {count} 次")
                    time.sleep(0.1 * (2**count))
                    continue
                break

            x, y = pyautogui.position()
            width, _ = get_screensize()
            pyautogui.click(width - 25, 115)
            pyautogui.moveTo(x, y)

            logger.info("Chromium 已启动并连接")
            return True

        except Exception as e:
            logger.error(f"启动 Chromium 失败: {e}")
            await self.stop_async()
            return False

    async def connect_to_cdp(self, url: str):
        """连接到 CDP"""
        self.cdp_url = url

    def _is_browser_running(self) -> bool:
        """检查浏览器是否在运行"""
        try:
            response = requests.get(self.cdp_url + "/json/version", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"检查浏览器是否在运行失败: {e}")
            return False

    async def get_cdp_tabs(self):
        """获取所有标签页"""
        try:
            response = requests.get(f"{self.cdp_url}/json/list", timeout=5)
            if response.status_code != 200:
                raise ValueError(f"获取标签页失败，状态码: {response.status_code}")

            tabs = response.json()
            # 过滤出 type 为 "page" 的标签页，这些是正常的网页标签页，而不是其他类型的标签页（如 DevTools 等）
            return [tab for tab in tabs if tab.get("type") == "page"]
        except Exception as e:
            raise ValueError(f"获取标签页失败: {e}")

    async def open_new_tab(self, url: str = "chrome://newtab/"):
        """打开新标签页"""
        try:
            # 使用 PUT 方法创建新标签页
            response = requests.put(
                f"{self.cdp_url}/json/new", json={"url": url}, timeout=5
            )
            if response.status_code != 200:
                print(response.text)
                raise Exception(f"打开新标签页失败，状态码: {response.status_code}")

            # 获取新标签页信息
            tab_info = response.json()
            logger.info(f"已打开新标签页: {tab_info.get('id')}")

            # 不在这里调用 maximize_window，让监控循环处理
            return True
        except Exception as e:
            logger.error(f"打开新标签页失败: {e}")
            return False

    async def _connect_to_tab(self, ws_url: str):
        """连接到标签页的 WebSocket"""
        try:
            # 如果已经存在连接，先关闭
            if ws_url in self.ws_connections:
                try:
                    await self.ws_connections[ws_url].close()
                except Exception as e:
                    logger.error(f"关闭 WebSocket 连接失败: {e}")
                del self.ws_connections[ws_url]

            # 创建新连接
            ws = await websockets.connect(
                ws_url,
                # ping_interval=None,  # 禁用自动ping
                close_timeout=5,
                max_size=None,
            )

            # 启用 Browser 域
            self.ws_connections[ws_url] = ws
            return ws
        except Exception as e:
            logger.error(f"连接到标签页 WebSocket 失败: {e}")
            return None

    async def maximize_window(self, tab_id: str):
        """最大化窗口"""
        ws_url = None
        try:
            # 获取标签页信息
            tabs = await self.get_cdp_tabs()
            tab_info = next((tab for tab in tabs if tab["id"] == tab_id), None)

            if not tab_info:
                logger.warning(f"找不到标签页: {tab_id}")
                return

            # 获取或创建 WebSocket 连接
            ws_url = tab_info["webSocketDebuggerUrl"]
            ws = self.ws_connections.get(ws_url)

            # 检查连接是否有效
            if not ws:
                logger.debug("WebSocket 连接已关闭，重新连接")
                ws = None
                if ws_url in self.ws_connections:
                    del self.ws_connections[ws_url]

            if not ws:
                logger.debug(f"创建新的 WebSocket 连接: {ws_url}")
                ws = await self._connect_to_tab(ws_url)
                if not ws:
                    logger.error("无法创建 WebSocket 连接")
                    return

            # 先获取当前窗口状态
            window_state = await self._send_cdp_command(
                ws,
                "Browser.getWindowForTarget",
                {"targetId": tab_id},  # 使用标签页ID而不是固定的windowId
                timeout=3.0,
            )

            if not window_state:
                logger.error("获取窗口状态失败")
                return

            window_id = window_state.get("windowId")
            if not window_id:
                logger.error("无法获取窗口ID")
                return

            bounds: Dict = window_state.get("bounds", {})
            current_state = bounds.get("windowState", "")

            # 获取当前窗口状态
            bounds_state = await self._send_cdp_command(
                ws, "Browser.getWindowBounds", {"windowId": window_id}, timeout=3.0
            )

            if not bounds_state:
                logger.error("获取窗口边界失败")
                return

            current_state = bounds_state.get("bounds", {}).get("windowState", "")
            logger.debug(f"当前窗口状态: {current_state}")

            # 如果窗口不是最大化状态，则进行最大化
            if current_state == "minimized":
                # 恢复窗口
                result = await self._send_cdp_command(
                    ws,
                    "Browser.setWindowBounds",
                    {"windowId": window_id, "bounds": {"windowState": "normal"}},
                    timeout=3.0,
                )
                logger.info("窗口已恢复")

            elif current_state != "maximized":
                # 最大化窗口
                result = await self._send_cdp_command(
                    ws,
                    "Browser.setWindowBounds",
                    {"windowId": window_id, "bounds": {"windowState": "maximized"}},
                    timeout=3.0,
                )

                if result is None:
                    logger.error("窗口最大化失败")

        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket 连接已关闭，将在下次循环重试")
            if ws_url in self.ws_connections:
                del self.ws_connections[ws_url]
        except Exception as e:
            logger.error(f"最大化窗口失败: {e}")
            if ws_url and ws_url in self.ws_connections:
                del self.ws_connections[ws_url]

    async def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                # 检查标签页
                tabs = await self.get_cdp_tabs()
                if not tabs:
                    logger.info("没有打开的标签页，创建新标签页...")
                    await self.open_new_tab()
                    await asyncio.sleep(1)  # 等待标签页创建完成
                    continue

                # 只对第一个标签页进行最大化检查
                await self.maximize_window(tabs[0]["id"])

            except Exception as e:
                logger.error(f"监控循环出错: {e}")
                # 清理所有连接
                for ws in self.ws_connections.values():
                    try:
                        await ws.close()
                    except Exception as e:
                        logger.error(f"关闭 WebSocket 连接失败: {e}")
                self.ws_connections.clear()
                try:
                    if self.browser_process:
                        self.browser_process.terminate()
                        self.browser_process.kill()
                except Exception as e:
                    logger.error(f"停止浏览器进程失败: {e}")
                await self.start()

            await asyncio.sleep(self.check_interval)

    async def start_monitoring(self):
        """开始监控"""
        if self.running:
            return

        self.running = True

        try:
            # 运行监控循环
            await self._monitor_loop()
        except Exception as e:
            logger.error(f"监控循环出错: {e}")
        finally:
            await self.stop_async()

    async def stop_async(self):
        """异步停止监控和浏览器"""
        self.running = False

        # 关闭所有 WebSocket 连接
        for ws in self.ws_connections.values():
            try:
                await ws.close()
            except Exception as e:
                logger.error(f"关闭 WebSocket 连接失败: {e}")
        self.ws_connections.clear()

        # 关闭浏览器进程
        if self.browser_process:
            try:
                self.browser_process.terminate()
                await asyncio.sleep(0.1)  # 给进程一些时间来终止
                if self.browser_process.poll() is None:
                    self.browser_process.kill()
            except Exception as e:
                logger.error(f"停止浏览器进程失败: {e}")
            self.browser_process = None

        logger.info("监控已停止")

    def stop(self):
        """同步停止监控和浏览器"""
        self.running = False

        try:
            # 获取当前事件循环
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果循环正在运行，使用 run_coroutine_threadsafe
                future = asyncio.run_coroutine_threadsafe(self.stop_async(), loop)
                future.result(timeout=5)  # 等待停止完成
            else:
                # 如果循环没有运行，直接运行
                loop.run_until_complete(self.stop_async())
        except Exception as e:
            logger.error(f"停止时出错: {e}")
            # 强制停止进程
            if self.browser_process:
                self.browser_process.kill()

    async def set_screen_resolution(self, width: int, height: int):
        """通过 CDP 协议设置浏览器视窗大小"""
        tabs = await self.get_cdp_tabs()
        tab_info = next((tab for tab in tabs if tab["type"] == "page"), None)
        if not tab_info:
            raise ValueError("没有找到标签页")
        ws_url = tab_info["webSocketDebuggerUrl"]
        ws = self.ws_connections.get(ws_url)
        if not ws:
            ws = await self._connect_to_tab(ws_url)
            if not ws:
                raise ValueError("无法连接到标签页的 WebSocket")

        # 先获取窗口ID
        window_state = await self._send_cdp_command(
            ws,
            "Browser.getWindowForTarget",
            {"targetId": tab_info["id"]},
            timeout=3.0,
        )

        if not window_state:
            raise ValueError("获取窗口状态失败")

        window_id = window_state.get("windowId")
        if not window_id:
            raise ValueError("无法获取窗口ID")

        # 设置窗口大小
        await self._send_cdp_command(
            ws,
            "Browser.setWindowBounds",
            {
                "windowId": window_id,
                "bounds": {"width": width, "height": height, "windowState": "normal"},
            },
        )


def wait_for_display(display=None, timeout=60):
    """等待 X11 显示服务器准备就绪"""
    if display is None:
        display = os.getenv("DISPLAY", ":99")

    logger.info(f"等待显示服务器 {display} 准备就绪...")

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # 尝试连接到 X11 显示服务器
            from Xlib import display as xlib_display

            d = xlib_display.Display(display)
            d.close()
            logger.info(f"显示服务器 {display} 已准备就绪")
            return True
        except Exception as e:
            logger.debug(f"显示服务器未就绪: {e}")
            time.sleep(0.5)

    logger.error(f"超时：显示服务器 {display} 在 {timeout} 秒内未准备就绪")
    return False


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Browser Guard - Monitor and manage browser instances"
    )
    parser.add_argument(
        "--wait-display",
        action="store_true",
        help="Wait for X11 display server to be ready",
    )
    parser.add_argument(
        "--monitor", action="store_true", help="Start browser monitoring"
    )
    parser.add_argument(
        "--display",
        type=str,
        default=None,
        help="X11 display to use (default: from DISPLAY env or :99)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Timeout in seconds for display wait (default: 60)",
    )

    args = parser.parse_args()

    if args.wait_display:
        success = wait_for_display(display=args.display, timeout=args.timeout)
        if not success:
            sys.exit(1)
        logger.info("Display server is ready")

    if args.monitor:

        async def run_monitor():
            if os.getenv("USE_CDP", "false").lower() == "true":
                browser_guard = BrowserCDPGuard()
            else:
                browser_guard = BrowserGuard()

            await browser_guard.start()
            await browser_guard.start_monitoring()

        import asyncio

        try:
            asyncio.run(run_monitor())
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            sys.exit(1)
