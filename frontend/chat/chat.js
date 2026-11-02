
    "use strict";

    // 1. 개발 중에는 백엔드가 없으므로 null로 둔다.
    // 추후 FastAPI 추천 서비스의 API 경로로 변경한다. (예: "/api/chat/messages")
    // API는 {conversation_id, message}를 받고 {reply, playlist} 형태의 JSON을 응답한다고 가정한다.
    // 실제 백엔드 계약이 정해지면 sendMessageToServer()의 요청·응답 필드를 일치시켜야 한다.
    const CHAT_MODE_SONG_ENDPOINT = "http://localhost:8000/chat/song";
    const CHAT_MODE_SENTENCE_ENDPOINT = "http://localhost:8000/chat/sentence";

    // 2. 이 HTML 단독 실행 시에도 대화 전환을 확인하도록 브라우저에만 저장한다.
    // 제출용 로그인 세션/서버 저장 기능과는 무관하다.
    const STORAGE_KEY = "melo_chat_sessions_v1";
    const ACTIVE_KEY = "melo_active_chat_v1";

    const $ = (selector) => document.querySelector(selector);
    const list = $("#conversationList"); //left sidebar nav tag
    const chat = $("#chatContent"); //채팅 메시지 출력 영역 div
    const chatScroll = $("#chatScroll");// 채팅메시지 출력 영역 section
    const input = $("#messageInput"); // 메시지 입력 textarea
    const mode = $(".mode-option");
    const buttons = document.querySelectorAll(".mode-option");
    const messageInput = document.querySelector("#messageInput");
    let toastTimer;
    let inputMode = "sentence";

    function setupModeSwitch() {

        buttons.forEach((button) => {
            button.addEventListener("click", () => {

                inputMode = button.dataset.mode;

                buttons.forEach((btn) => {
                    btn.classList.toggle("active", btn === button);
                });

                if (inputMode === "song") {
                    messageInput.placeholder = "노래 제목을 입력해 주세요...";
                } else {
                    messageInput.placeholder = "원하는 분위기나 노래를 말해 주세요...";
                }
            });
        });
    }

    setupModeSwitch();


    // 새로운 채팅창에 대한 객체 생성
    function makeConversation() {
      return {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`, 
        title: "새 플레이리스트", 
        messages: [], 
        playlist: [] };
    }


    //
    function readSavedChats() {
      try {
        const result = JSON.parse(localStorage.getItem(STORAGE_KEY));
        return Array.isArray(result) ? result.filter(item => item && item.id && Array.isArray(item.messages)) : [];
      } catch (_) {
        // 저장 데이터가 손상되었거나 읽을 수 없으면 빈 목록으로 시작한다.
        return [];
      }
    }

    let conversations = readSavedChats();
    if (conversations.length === 0){
        conversations = [makeConversation()]
    }

    let activeId = localStorage.getItem(ACTIVE_KEY);
    if (!conversations.some(item => item.id === activeId)) {
        activeId = conversations[0].id;
    }
    const current = () => conversations.find(item => item.id === activeId);

    function save() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
            localStorage.setItem(ACTIVE_KEY, activeId);
        } catch (_) {
            showToast("브라우저 저장 공간을 사용할 수 없습니다.");
        }
    }

    // 3. 안전한 DOM 조작: 사용자 메시지를 innerHTML로 해석하지 않고 textContent로 출력한다.
    // 왼쪽 sidebar에 대한 함수
    function renderSidebar() {
        list.replaceChildren();

        for (const conversation of conversations) {
            const button = document.createElement("button");

            button.type = "button";
            button.className = `conversation-item${conversation.id === activeId ? " active" : ""}`;
            //button에 css 연결
            button.setAttribute("aria-current", conversation.id === activeId ? "page" : "false");

            const icon = document.createElement("span");
            icon.className = "bubble-icon";
            icon.textContent = "☰";

            const title = document.createElement("span");
            title.className = "conversation-title";
            title.textContent = conversation.title;
            
            button.append(icon, title);
                button.addEventListener("click", () => {activeId = conversation.id; save(); render(); closePanels(); });
            list.append(button);
        }
    }

    function renderWelcome() {
        chat.classList.add("welcome");
        chat.replaceChildren();
        
        const icon = document.createElement("div");
        icon.className = "welcome-orbit";
        icon.textContent = "♫";
        
        const heading = document.createElement("h1");
        heading.textContent = "좋은 음악은 대화에서 시작돼요.";
        
        const description = document.createElement("p");
        description.textContent = "오늘의 기분과 취향을 이야기해 주세요. 한 번의 대화를 이어가며 나만의 플레이리스트를 완성할 수 있어요.";
        
        const suggestions = document.createElement("div");
        suggestions.className = "suggestions";
        
        const prompts = [
        ["☀", "기분 좋아지는 출근길 음악"],
        ["☾", "늦은 밤 산책에 어울리는 곡"],
        ["✎", "집중할 때 듣는 잔잔한 음악"],
        ["✦", "요즘 취향을 새롭게 발견하고 싶어"]
        ];
        
        for (const [symbol, text] of prompts) {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "suggestion";
            const emoji = document.createElement("span");
            emoji.textContent = symbol;
            button.append(emoji, document.createTextNode(text));
                button.addEventListener("click", () => {input.value = text; updateComposer(); input.focus(); });
            suggestions.append(button);
        }
        
        chat.append(icon, heading, description, suggestions);
    }

    function renderMessages(messages) {
        chat.classList.remove("welcome");
        chat.replaceChildren();
        
        const container = document.createElement("div");
        container.className = "messages";
        
        for (const message of messages) {
            const row = document.createElement("div");
            const user = message.role === "user";
            row.className = `message${user ? " user" : ""}`;
            
            const group = document.createElement("div");
            const label = document.createElement("div");
            label.className = "message-label";
            label.textContent = user ? "나" : "Melo";
            
            const bubble = document.createElement("div");
            bubble.className = "message-bubble";
            bubble.textContent = String(message.text ?? "");
            
            group.append(label, bubble);

            console.log("message.text:", message.text); 
            console.log("type:", typeof message.text);      
            
            if (!user) {
                const avatar = document.createElement("div");
                avatar.className = "message-avatar";
                avatar.textContent = "♫";
                row.append(avatar);
            }

            row.append(group);
            container.append(row);
        }

        chat.append(container);
    }

    //오른쪽 sidebar
    function renderPlaylist(conversation) {
        const tracks = Array.isArray(conversation.playlist) ? conversation.playlist : [];
        
        $("#playlistTitle").textContent = conversation.title;
        $("#trackCount").textContent = `♫ ${tracks.length}곡 수록`;
        $("#trackCountSmall").textContent = `${tracks.length} TRACKS`;
        
        const trackList = $("#trackList");
        
        trackList.replaceChildren();
        if (tracks.length === 0) {
            const empty = document.createElement("div");
            empty.className = "track-empty";
            empty.textContent = "아직 담긴 곡이 없어요.\n추천 결과가 나오면 여기에 쌓입니다.";
            empty.style.whiteSpace = "pre-line";
            trackList.append(empty);
            return;
        }
        
        tracks.forEach((track) => {
            const item = document.createElement("div");
            item.className = "track-item";
            
            const art = document.createElement("div");
            art.className = "track-art";
            art.textContent = "♪";
            
            const info = document.createElement("div");
            info.className = "track-info";
            
            const name = document.createElement("div");
            name.className = "track-name";
            name.textContent = track.title ?? "제목 없음";
            
            const artist = document.createElement("div");
            artist.className = "track-artist";
            artist.textContent = track.artist ?? "아티스트 미상";
            
            info.append(name, artist);
            item.append(art, info);
            trackList.append(item);
        });
    }

    function render() {
        const conversation = current();
        
        if (!conversation) return;
            renderSidebar();
            
            $("#currentTitle").textContent = conversation.title;
            
            if (conversation.messages.length === 0) renderWelcome();
            else renderMessages(conversation.messages);
            
            renderPlaylist(conversation);
            chatScroll.scrollTop = chatScroll.scrollHeight;
        }

        function showToast(message) {
            const toast = $("#toast");
            
            toast.textContent = message;
            toast.classList.add("show");
            
            clearTimeout(toastTimer);
            toastTimer = setTimeout(() => toast.classList.remove("show"), 3500);
    }

    //서버와의 통신을 담당하는 비동기 함수
    async function telemetry(conversationId, message) {
        let endpoint = null

        if (inputMode == "song"){
            endpoint = CHAT_MODE_SONG_ENDPOINT
        }
        else{
            endpoint = CHAT_MODE_SENTENCE_ENDPOINT
        }
    
        if (endpoint ==null){
            //에러코드 발생
        }

        try{
            const response = await fetch(endpoint, {
                        method: "POST",
                        headers: {"Content-Type": "application/json" },
                        credentials: "same-origin", // 향후 Redis 세션 식별용 쿠키를 자동 전송
                        body: JSON.stringify({
                            conversation_id: conversationId, 
                            message : message,
                        })  
                    })
        }
        catch(_){
            showToast("백엔드 요청 중 에러 발생")
        }

        if(!response.ok) throw new Error(`HTTP ${response.status}`)
        const data = await response.json()

        return data
    } 

    // 4. 서버 연결부: 실제 API가 생기기 전에는 답변을 만들어내지 않는다.
    async function sendMessageToServer(conversationId, message) {
            
            // 백엔드 서버와의 http 통신
            data = telemetry(conversationId, message)
            
            // API 결과가 비동기로 도착했을 때도 요청한 대화에 붙여야 한다.
            const target = conversations.find(item => item.id === conversationId);
            if (!target) return;
            

            if (data) target.messages.push({
                role: "assistant", 
                text: data.map(
                    item => item.artist + " - " + item.track
                ).join("\n")
            });
            if (Array.isArray(data)) target.playlist = data.map(
                    item => item.artist + " - " + item.track
                ).join("\n");

            console.log(target.messages)
            
            save();
            render();
    }

    function updateComposer() {
        $("#sendButton").disabled = input.value.trim().length === 0;
        input.style.height = "auto";
        input.style.height = `${Math.min(input.scrollHeight, 160)}px`;
    }

        $("#messageForm").addEventListener("submit", (event) => {
        
            event.preventDefault(); // form의 기본 새로고침 방지
            const text = input.value.trim();
    
            if (!text) return;
            const conversation = current();
            conversation.messages.push({role: "user", text });
        
            if (conversation.messages.length === 1) conversation.title = text.length > 24 ? text.slice(0, 24) + "…" : text;
            
            save();
            render();
    
            input.value = "";
    
            updateComposer();
    
            if (!CHAT_ENDPOINT) showToast("대화는 저장됐어요. 추천 서버는 아직 연결되지 않았습니다.");
    
            else sendMessageToServer(conversation.id, text);
    
        });

        input.addEventListener("input", updateComposer);
        input.addEventListener("keydown", (event) => {
      
            if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
        
                event.preventDefault();
    
                $("#messageForm").requestSubmit();
      
            }
    });

    
    $("#newChatButton").addEventListener("click", () => {
      
        const created = makeConversation();
    
        conversations.unshift(created);
    
        activeId = created.id;
    
        save();
        render();
        closePanels();
        input.focus();
    });

    
    $("#deleteChat").addEventListener("click", () => {
      // 실수로 이전 대화가 사라지지 않도록 삭제 여부를 확인한다.
      
      if (!confirm("현재 대화를 삭제하시겠어요? 이 브라우저의 저장 기록에서도 삭제됩니다.")) return;
      conversations = conversations.filter(item => item.id !== activeId);
    
      if (conversations.length === 0) conversations = [makeConversation()];
    
      activeId = conversations[0].id;
    
      save();
      render();
    });

    function closePanels() {
        $("#sidebar").classList.remove("open");
        $("#playlistPanel").classList.remove("open"); 
        $("#overlay").classList.remove("show");
    }

    
    $("#openSidebar").addEventListener("click", () => {
        closePanels();
        $("#sidebar").classList.add("open"); 
        $("#overlay").classList.add("show");
    });

    $("#openPlaylist").addEventListener("click", () => {
        closePanels();
    
        $("#playlistPanel").classList.add("open");
    
        $("#overlay").classList.add("show");
    });
    
    $("#overlay").addEventListener("click", closePanels);
    document.addEventListener("keydown", event => { if (event.key === "Escape") closePanels(); });

    // 5. 새로고침 시에도 이전 대화 목록을 복원한다.
    save();
    render();
    updateComposer();
