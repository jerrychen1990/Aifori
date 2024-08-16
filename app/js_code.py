html_code = """<!DOCTYPE html>
<html>


<body>
    <style>
        .invisible-button {
            opacity: 0;
            /* 完全透明 */
            position: absolute;
            /* 确保按钮不影响布局 */
            top: 10px;
            /* 位置调整 */
            left: 10px;
            /* 位置调整 */
        }
    </style>

    <button id="myButton" onclick="onSendMessage()">发送消息</button>

</body>
<script>
    var audioQueue = [];
    var context = new (window.AudioContext || window.webkitAudioContext)();
    var isPlaying = false;

    var objSocket = new WebSocket('ws://127.0.0.1:9100/assistant/play_music_stream');
    objSocket.onopen = function (evt) {
        onOpen(evt);
    };
    objSocket.onclose = function (evt) {
        console.info('Connection closed.');
        onClose(evt);
    };
    objSocket.onmessage = function (evt) {
        onMessage(evt);
    };
    objSocket.onerror = function (evt) {
        onError(evt);
    };

    function onOpen(evt) {
        console.log("Connected to WebSocket server.");
        // triggerButtonClick();

    }

    function onClose(evt) {
        console.log("Disconnected");
    }

    function onError(evt) {
        console.log('Error occurred: ' + evt.data);
    }

    function onMessage(evt) {
        const decoder = new TextDecoder('utf-8');

        // var chunk = decoder.decode(evt.data);
        // console.log('Retrieved data from server: ' + chunk.substring(0,20));
        // const obj = JSON.parse(chunk);
        // console.log(obj["voice_chunk"]);

        // console.log('Retrieved data from server: ' + evt.data);
        // console.log('chunk size: ' + getByteLength(evt.data));

        var reader = new FileReader();
        reader.readAsArrayBuffer(evt.data);
        reader.onload = function () {
            audioQueue.push(this.result);
            if (!isPlaying) {
                playNextAudio();
            }
        };
    }

    function playSound(buffer) {
        var source = context.createBufferSource(); // 创建一个声音源
        source.buffer = buffer; // 告诉该源播放何物
        source.connect(context.destination); //将该源与硬件相连
        source.start(0); // 开始播放
    };


    function onSendMessage() {
        const message = {
            "user_id": "test_user",
            "music_desc": "你好呀，我的名字叫Aifori",
        };
        objSocket.send(JSON.stringify(message));
        console.log('Sent message to server: ' + JSON.stringify(message));	//发送消息

    };

    // navigator.mediaDevices.getUserMedia({ audio: true });


    function playNextAudio() {
        if (audioQueue.length === 0) {
            isPlaying = false;
            return;
        }

        isPlaying = true;
        var audioData = audioQueue.shift();

        context.decodeAudioData(audioData, function (buffer) {
            var source = context.createBufferSource();
            source.buffer = buffer;
            source.connect(context.destination);
            source.onended = function () {
                playNextAudio();
            };
            source.start(0);
        }, function (e) {
            console.error("Error with decoding audio data: " + e.err);
            playNextAudio();
        });
    };

    function triggerButtonClick() {
        // 获取按钮元素
        const button = document.getElementById('myButton');
        // 模拟点击事件
        button.click();
    }
    // triggerButtonClick();
</script>

</html>
"""
