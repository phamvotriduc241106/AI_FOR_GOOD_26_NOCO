# SỔ TAY NGÀY THI: AI_FOR_GOOD

Đây là **file duy nhất** bạn cần mở trong suốt cuộc thi. Đi từ trên xuống dưới, tick `[x]` khi xong.
Mọi lệnh đều đã điền sẵn tên, chỉ việc copy–paste. Lệnh nào lỗi: xem **mục 8**.

- Hôm nay ban tổ chức phát **đề giấy**, nên luồng chính là: đề giấy → file `.txt` → chạy phân tích ngay
  (**mục 4.2**). Phần chấm điểm, pitch, nộp bài sẽ được **ghi âm** và chạy thêm một lần (**mục 4.10**).
- **Mục 5** do công cụ tự sinh từ `docs/TASKS.md` (`make lanes`): ai làm gì, việc nào song song, ai chờ ai,
  lệnh và lời nhắc cho từng người. Đừng sửa tay trong khối đó.
- Mở file này bằng trình soạn thảo có xem trước Markdown. Muốn xem đẹp trên trình duyệt: commit + push,
  rồi mở `https://github.com/Nguyen-Le-Tuan/AI_FOR_GOOD/blob/main/docs/DAY_OF.md`.

## 1. Thông tin cố định

| Mục | Giá trị |d
|---|---|
| Repo của đội | `Nguyen-Le-Tuan/AI_FOR_GOOD` (private), tạo từ template `Nguyen-Le-Tuan/hackkit` |
| Thư mục trên máy tôi | `~/Desktop/AI_FOR_GOOD` (worktree kế hoạch: `~/Desktop/AI_FOR_GOOD-agent`) |
| File đề (đã chuyển sang chữ) | `docs/AI_for_Good_Hackathon_Full_Text.txt`: 3 challenge là **ACV (Auctions + Copart)**, **Against All Oddz Animal Alliance (AAO)**, **NOCO** |
| **Tôi** | `Nguyen-Le-Tuan`: điều phối, quyết định, review và merge PR, thuyết trình |
| **Anh-08** | dùng **Claude Code**, người merge dự phòng |
| **NguyenQBao** | dùng **Codex**, QA và chạy demo |
| **phamvotriduc241106** | dùng **Codex** (vai trò `codex-2`): **review chéo (R1), pitch/Devpost, hỏi ban tổ chức/đối tác, xác nhận đội, đối chiếu đề giấy với file chữ, tìm dữ liệu công khai** |

Ba người dùng agent: Anh-08 (Claude Code), NguyenQBao (Codex), phamvotriduc241106 (Codex, vai trò `codex-2`).
Quy tắc: tối đa **hai** agent *viết code* cùng lúc, trên các file khác nhau; agent thứ ba dùng cho review chéo,
dữ liệu/eval hoặc giao diện. Đổi ai làm gì: sửa bảng **Team** trong `docs/TASKS.md`, rồi `make lanes`.

## 2. Chuẩn bị chung (cho cuộc thi sau cũng dùng được)

- [ ] Đăng nhập đủ: `claude --version`, `codex login status`, `gh auth status`.
- [ ] Template đang xanh: `gh run list -R Nguyen-Le-Tuan/hackkit --limit 1` ra `completed success`.
- [ ] Laptop: sạc đầy, tắt cập nhật tự động. Có khóa Groq (nằm trong console Groq, **không** dán vào chat hay commit).
- [ ] (Tùy chọn) Phương án chạy cục bộ nếu đối tác không cho gửi dữ liệu sang dịch vụ AI: cài Ollama và kéo
      một model nhỏ (hiện **chưa cài**).

## 3. Thiết lập repo (một lần)

**3.1 Mạng.** [ ] `ping -c 2 github.com` có phản hồi.

**3.2 Tạo repo của đội từ template và clone** (bỏ qua nếu `~/Desktop/AI_FOR_GOOD` đã có).
```bash
cd ~/Desktop && gh repo create AI_FOR_GOOD --template Nguyen-Le-Tuan/hackkit --private --clone
```

**3.3 Mời 3 bạn.**
```bash
for u in NguyenQBao Anh-08 phamvotriduc241106; do gh api -X PUT repos/Nguyen-Le-Tuan/AI_FOR_GOOD/collaborators/$u -f permission=push --silent; done
```
- [ ] Gửi tin nhắn này cho cả ba:
```text
Mình đã mời 3 bạn vào repo AI_FOR_GOOD. Làm 3 việc, xong nhắn "OK":
1) Chấp nhận lời mời: https://github.com/Nguyen-Le-Tuan/AI_FOR_GOOD/invitations
2) Chạy: git clone https://github.com/Nguyen-Le-Tuan/AI_FOR_GOOD.git && cd AI_FOR_GOOD && make setup && source .venv/bin/activate && make test
3) Đăng nhập agent: Anh-08 chạy `claude`; NguyenQBao và phamvotriduc241106 chạy `codex`.
Chưa cần điền khóa. Đừng push gì lên main.
```
- [ ] Anh-08: OK. [ ] NguyenQBao: OK. [ ] phamvotriduc241106: OK.

**3.4 Cài đặt của tôi. CHƯA điền khóa Groq.**
```bash
cd ~/Desktop/AI_FOR_GOOD && make setup && source .venv/bin/activate
make test && make lint
```
- [ ] `make test` và `make lint` đều xanh.
- **Vì sao chưa điền khóa:** agent trong `orchestrate.sh` chạy cạnh repo và **đọc được `../.env`** (đã kiểm
  chứng với cả Claude và Codex). Script từ chối chạy nếu `.env` có khóa. Khóa chỉ điền ở **mục 4.11**, sau
  lần chạy cuối cùng. Các việc T1 đến T3 chạy được với provider `fake`, chưa cần khóa.

**3.5 Đọc luật của cuộc thi (không bỏ qua).**
- [ ] Đội chọn challenge thế nào, có được đổi không, hạn chọn là khi nào?
- [ ] Có được dùng code/template có sẵn không? Có phải khai báo template và công cụ AI không?
- [ ] **Dữ liệu của đối tác/nhà tài trợ: có được gửi sang dịch vụ AI bên thứ ba (Claude, Codex, Groq) không?**
      Chưa có câu trả lời "được" thì **chỉ dùng dữ liệu giả**: không dán dữ liệu thật vào prompt, không để vào repo.
- [ ] Hạn xác nhận đội, và đại diện đối tác ở bàn đến mấy giờ?
- [ ] Hạn nộp Devpost, giờ đóng băng, thể thức pitch (mấy phút) và tiêu chí chấm.

**3.6 Preflight (kiểm tra máy, 1 phút).**
```bash
cd ~/Desktop/AI_FOR_GOOD && ./scripts/orchestrate.sh --check --transcript docs/AI_for_Good_Hackathon_Full_Text.txt
```
- [ ] Phải thấy `OK: ... .env holds no filled-in secret values`, `OK: Claude`, `OK: fallback claude-opus-5-5`, `OK: Codex`.
      Có `WARN` hoặc lỗi thì sửa theo mục 8 **trước khi** đi tiếp.

## 4. Luồng đề giấy: từ lúc có đề đến khi khóa hợp đồng

**4.1 Chuẩn bị file đề.**
- [ ] File chữ nằm ở `docs/AI_for_Good_Hackathon_Full_Text.txt`: `ls -la ~/Desktop/AI_FOR_GOOD/docs/AI_for_Good_Hackathon_Full_Text.txt`.
- [ ] **phamvotriduc241106 đối chiếu file chữ với đề giấy** (hạn chót, tỷ lệ/điểm, tên, số liệu, điều kiện bắt buộc,
      điểm cộng). File này do AI chép từ ảnh nên có thể sai hoặc thiếu. Gửi danh sách chỗ sai cho tôi. Có chỗ quan
      trọng thì sửa file chữ rồi chạy lại 4.2 (khoảng 5 phút).

**4.2 Chạy phân tích đề ngay** (không cần ghi âm, không cần khóa màn hình):
```bash
cd ~/Desktop/AI_FOR_GOOD && ./scripts/orchestrate.sh --now --transcript docs/AI_for_Good_Hackathon_Full_Text.txt --document --no-lid-guard
```
- Mất khoảng 5 phút: đọc đề, phê bình, lập kế hoạch cho từng challenge, rà soát kế hoạch. Có thử lại và dự phòng Opus.
- Muốn xem tiến độ: `cat ~/Desktop/AI_FOR_GOOD-agent/docs/agent/STATUS.md`. Dừng khẩn: `touch ~/Desktop/AI_FOR_GOOD/STOP`.
- [ ] Đã chạy lúc: ______

**4.3 Trong 5 phút chờ, cả bốn người làm song song.**
- [ ] **Tôi:** đọc đề giấy của cả 3 challenge, ghi câu hỏi cần hỏi ban tổ chức.
- [ ] **phamvotriduc241106:** làm 4.1, rồi đi hỏi ban tổ chức/đối tác (gửi tin dưới) và xác nhận đội ở bàn tiếp tân.
- [ ] **Anh-08 và NguyenQBao:** đọc 3 challenge, mỗi người chọn **một** challenge mình thấy làm được trong vài giờ bằng
      hackkit (mô hình AI trích xuất, quy tắc thường tính toán) và nói lý do trong 2 dòng.
```text
@phamvotriduc241106: đi hỏi ban tổ chức/đối tác ngay, ghi lại NGUYÊN VĂN câu trả lời, gửi lại trong 10 phút:
1) Đội chọn challenge thế nào, hạn chọn là khi nào, có được đổi không?
2) Dữ liệu/API đối tác cung cấp là gì, lấy ở đâu? Có được gửi sang Claude/Codex/Groq (dịch vụ AI bên thứ ba) không?
3) Người dùng thật của họ là ai, hôm nay họ làm việc đó thế nào? Họ muốn thấy gì nhất trong demo?
4) Tiêu chí chấm điểm, thể thức pitch (mấy phút), cách nộp bài, hạn nộp?
5) Xác nhận đội mình và hạn xác nhận đội.
```

**4.4 Đọc kết quả của máy.**
```bash
cd ~/Desktop/AI_FOR_GOOD-agent/docs/agent
cat STATUS.md
less BRIEF.md        # q để thoát
less PLAN_REVIEW.md  # checklist 5 dòng ở cuối
```
- [ ] `STATUS.md` có dòng `DONE`, cả 4 file có dấu `[x]`, không có file nào bị sửa ngoài `docs/agent`.
- [ ] **Khối "Secret scan" phải là `clean`**: `grep -A4 "Secret scan" STATUS.md`. Nếu có `ALERT`: **không merge** `agent/plan` (mục 8).
- [ ] `BRIEF.md` khớp đề giấy: 3 challenge, tên đối tác, câu hỏi chính, điểm cộng. Đối chiếu số liệu với file đề.
- [ ] Ghi lại mục "Uncertain or missing" của BRIEF để hỏi ban tổ chức.

**4.5 Chọn challenge và plan (khoảng 10 phút, cả bốn người cùng quyết, sau khi có câu trả lời ở 4.3).**
- [ ] Tiêu chí: (1) khớp tiêu chí chấm, (2) **một** người dùng, một đường demo rõ, (3) dùng dữ liệu/API công khai hoặc
      của đối tác nếu được phép, (4) làm trọn trong thời gian còn lại, (5) demo ổn định.
- [ ] Challenge và plan đã chọn: ______ (ghi vào đây)
- [ ] Đưa tài liệu kế hoạch vào `main`: `cd ~/Desktop/AI_FOR_GOOD && git switch main && git merge agent/plan`

**4.6 Soạn `docs/spec.md` (tôi duyệt từng dòng).** Mở Claude Code trong repo (`claude`) rồi dán, thay `X` bằng
challenge/plan đã chọn:
```text
Đọc docs/agent/BRIEF.md, docs/agent/PLAN_REVIEW.md, docs/agent/PLANS.md và docs/AI_for_Good_Hackathon_Full_Text.txt.
Tôi chọn challenge X, theo bản rút gọn trong PLAN_REVIEW. Soạn docs/spec.md theo đúng 6 mục của file mẫu, thêm
câu trả lời của đối tác dưới đây (kể cả việc dữ liệu có được gửi sang dịch vụ AI không): <dán câu trả lời>.
Chỉ ghi điều có trong tài liệu hoặc câu trả lời, ghi rõ chỗ chưa chắc. Không viết code.
```
- [ ] Đã đọc và sửa `docs/spec.md` (vấn đề, **một** người dùng, đường demo từng bước, ngoài phạm vi).

**4.7 Điền `AGENTS.md` (khối Project) và `docs/TASKS.md` (khóa hợp đồng).** Vẫn trong Claude Code:
```text
Từ docs/spec.md: (1) điền khối "Project (FILL ON EVENT DAY)" trong AGENTS.md; (2) điền docs/TASKS.md:
Contract (feature key, schema, rules, file mẫu, eval) và bảng Tasks theo bốn việc của kế hoạch đã chọn trong
PLAN_REVIEW. Giữ nguyên bảng Team (bốn người; ba vai trò agent: claude = Anh-08, codex = NguyenQBao, codex-2 =
phamvotriduc241106; chỉ hai agent viết code cùng lúc, codex-2 làm review chéo, dữ liệu/eval hoặc giao diện). Quy ước: T1 là khung đăng ký tính năng, merge trong ~10 phút;
việc chỉ cần T1 để chạy eval thì ghi phụ thuộc mềm `T1~`; các việc chạy song song phải sửa file KHÁC nhau.
Việc không cần agent (pitch, Devpost, tìm dữ liệu công khai, hỏi đối tác) giao cho vai trò human-C hoặc
researcher. Không viết code.
```
- [ ] Đã đọc kỹ **Contract** và cột **Files it may touch**. Hai việc cùng đợt không được trùng file.
- [ ] Bảng **Team** đúng người, đúng công cụ (kể cả `phamvotriduc241106`).
- [ ] `docs/PITCH.md`: điền tiêu chí chấm và "khoảnh khắc demo chiến thắng" (chốt sau lần ghi âm, mục 4.10).

**4.8 Khóa quyết định và sinh luồng việc.**
```bash
cd ~/Desktop/AI_FOR_GOOD && make lanes
git add -A && git commit -m "docs: spec, tasks, luồng việc" && git push origin main
```
- [ ] `make lanes` không báo cảnh báo `⚠` (nếu có: sửa `docs/TASKS.md` rồi chạy lại).

**4.9 Giao việc cho 4 người.** Mở **mục 5**, copy "Tin nhắn cho nhóm chat" gửi cả nhóm. Mỗi người chạy lệnh trong phần
của mình (ai đã clone ở 3.3 chỉ cần `git pull origin main`).
- [ ] Đã gửi tin nhắn giao việc.

**4.10 Lần chạy 2: ghi âm phần chấm điểm, pitch, nộp bài.** Khi ban tổ chức nói về chấm điểm/pitch (bật ghi âm
từ đầu phần đó). **Phiên ghi âm cứ để chạy, đừng tắt server**: lệnh dưới chỉ đọc transcript hiện có qua API.

0. **Nếu `.env` đang có khóa Groq** (script sẽ từ chối chạy): tạm xóa khóa, rồi điền lại ở 4.11:
```bash
cd ~/Desktop/AI_FOR_GOOD && sed -i 's|^GROQ_API_KEY=.*|GROQ_API_KEY=|; s|^LLM_PROVIDER=.*|LLM_PROVIDER=fake|' .env && python3 scripts/secret_scan.py --check-env
```
   Phải ra `no filled secret values`. Giữ khóa trong console Groq hoặc trình quản lý mật khẩu (không lưu bản sao
   trong thư mục home: agent đọc được).

1. Bật LectureBridge (terminal riêng, để chạy suốt):
```bash
cd ~/lecturebridge/lecturebridge
.venv/bin/python -m lecturebridge.live \
  --device cuda \
  --model distil-large-v3.5 \
  --language en \
  --data-dir /home/nguyenletuan/Desktop
```
   - [ ] Mở `http://127.0.0.1:8000`, **bật lưu bản ghi**, đặt laptop gần loa. Kiểm tra: `curl -s http://127.0.0.1:8000/health`.
2. Khi phần đó kết thúc, chạy (gộp **đề viết + bản ghi mới**, và dùng challenge đã chọn để kế hoạch tập trung):
```bash
cd ~/Desktop/AI_FOR_GOOD && ./scripts/orchestrate.sh --now --lecturebridge --with-file docs/AI_for_Good_Hackathon_Full_Text.txt --chosen "X" --no-lid-guard
```
   Thay `X` bằng challenge đã chọn (tối đa 300 ký tự). Muốn hẹn giờ và khóa màn hình để rời đi:
   `--at 11:00 --lock` thay cho `--now`, và bỏ `--no-lid-guard`.
3. Kết quả cũ không mất: được lưu ở `docs/agent/archive/<giờ>/`. Kết quả mới có thêm **tiêu chí chấm, thể thức pitch,
   hạn nộp**.
- [ ] Đã đọc BRIEF mới, **cập nhật `docs/spec.md` và `docs/PITCH.md`** với tiêu chí chấm và thể thức pitch.
- [ ] `STATUS.md` mới: có `DONE` và Secret scan `clean`.
- Lưu ý: lần chạy này cũng **từ chối chạy nếu `.env` có khóa**. Vì thế **chưa điền khóa Groq** cho tới sau lần này.

**4.11 Điền khóa Groq. CHỈ sau lần chạy cuối cùng của `orchestrate.sh`** (khóa không hiện trên màn hình và không
nằm trong lịch sử lệnh):
```bash
cd ~/Desktop/AI_FOR_GOOD && read -rsp "Dán khóa Groq rồi Enter: " K && echo && sed -i "s|^LLM_PROVIDER=.*|LLM_PROVIDER=groq|; s|^GROQ_API_KEY=.*|GROQ_API_KEY=$K|" .env && unset K
```
- [ ] Đã điền khóa. (Muốn chạy lại `orchestrate.sh` sau này thì phải để trống `GROQ_API_KEY=` trước.)

## 5. LUỒNG VIỆC HIỆN TẠI (tự sinh, đừng sửa tay)

<!-- LANES:START -->
Chưa có dữ liệu. Sau bước **4.8** chạy `make lanes`: khối này sẽ hiện ai làm gì, việc nào song song,
ai chờ ai, và lệnh/lời nhắc copy–paste cho từng người.
<!-- LANES:END -->

## 6. Vòng lặp điều phối của tôi

Mỗi khi có thay đổi, cập nhật trạng thái **một dòng** rồi đọc lại mục 5 (phần "Ngay bây giờ"):

| Sự kiện | Lệnh |
|---|---|
| Ai đó báo bắt đầu một việc | `make lanes SET="T1=doing"` |
| Ai đó mở PR | `make lanes SET="T1=review"` |
| Tôi merge PR xong | `make lanes SET="T1=merged"` rồi báo người đang chờ (mục 5 liệt kê) |
| Nhiều thay đổi cùng lúc | `make lanes SET="T1=merged T2=doing"` |

Quy trình mỗi PR:
```bash
cd ~/Desktop/AI_FOR_GOOD
gh pr list
gh pr checks <số PR> --watch          # chỉ merge khi xanh
gh pr merge <số PR> --merge
git switch main && git pull origin main && make test && make lint
```
- PR chậm hơn `main`? `gh api -X PUT repos/Nguyen-Le-Tuan/AI_FOR_GOOD/pulls/<số PR>/update-branch --silent`.
  ("Re-run jobs" không giúp vì dùng lại bản ghép cũ.)
- **Người merge dự phòng: Anh-08.** Khi tôi bận (hỏi đối tác, trình bày), Anh-08 merge theo đúng quy trình
  trên. Chỉ merge PR **xanh**, **không** merge PR của chính mình, và nhắn tôi sau mỗi lần merge để tôi chạy
  `make lanes SET=...`.
- **Quy tắc song song:** chỉ chạy song song khi (1) file không chồng nhau và (2) việc phụ thuộc đã merge.
  Việc quá ngắn (dưới ~10 phút của agent) thì để một agent làm liền, đỡ tốn công PR và merge.
- Cứ khoảng 30 phút nhìn lại "Ngay bây giờ" và dọn những việc đang chờ.
- Khi mọi việc của một đợt đã merge: `make demo` chạy thử một lượt.

## 7. Đóng băng và nộp bài

- [ ] **Trước hạn 1 giờ 30 phút: đóng băng.** Chỉ sửa lỗi, không thêm tính năng.
- [ ] `make test && make lint` đều xanh.
- [ ] **Làm nóng cache bằng model thật.** Laptop trình bày **phải chính là laptop làm bước này**: cache nằm ở
      `.cache/hackkit`, chỉ có trên máy đó và không lên git.
  1. `cd ~/Desktop/AI_FOR_GOOD && source .venv/bin/activate && LLM_PROVIDER=groq make run`
  2. Ở thanh bên, bấm **Clear saved results TRƯỚC**. Cache không phân biệt provider: kết quả của provider
     `fake` đã lưu (do `make demo` hay lúc tập) sẽ bị trả lại thay cho model thật (đã kiểm chứng).
  3. Chọn provider `groq`, chạy **từng input demo một lần**. Mỗi kết quả phải ghi `N model call(s)`
     (không phải `saved result`).
  4. Bật **Demo mode** ở thanh bên rồi chạy lại từng input: phải ghi `saved result` và không dùng mạng.
     (Hoặc mở bằng `DEMO_MODE=1 LLM_PROVIDER=groq make run`.)
  5. Input chưa từng được làm nóng sẽ báo lỗi "Demo mode is on and this input has no cached result":
     chỉ trình diễn đúng các input đã chạy.
  - Sửa `INSTRUCTIONS` hoặc schema thì cache cũ tự hết hiệu lực: phải làm nóng lại.
- [ ] `make demo` chỉ chạy bản **mẫu** với provider giả (tập offline). Đó **không** phải demo thật.
- [ ] Chạy một lần `LLM_PROVIDER=groq make eval`, ghi lại độ chính xác.
- [ ] Tập pitch 3 lần, quay video demo dự phòng.
- [ ] Điền `docs/PITCH.md`, hoàn tất Devpost **trước hạn ít nhất 30 phút**, ghi rõ đã dùng template
      `hackkit` và các công cụ AI.
- [ ] Thành viên đã được liệt kê, bài nộp đã bấm "submit".

## 8. Xử lý sự cố

| Triệu chứng | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| `make test`: `pytest: not found` | Chưa kích hoạt môi trường ảo | `source .venv/bin/activate` |
| `--check`: Codex lỗi đăng nhập hoặc model | Chưa đăng nhập hoặc bản cũ | `codex login`, `codex --version` |
| `--check`: Claude lỗi | Chưa đăng nhập | chạy `claude` một lần và đăng nhập |
| `--check --lecturebridge`: LectureBridge không truy cập được | App chưa chạy | mục 4.10, bước 1 |
| Script chờ rồi báo "no ... status=recording" | Chưa bật lưu bản ghi hoặc đã dừng ghi | bật ghi âm (mục 4.10) rồi chạy lại `--now` |
| BRIEF nói không có nội dung của đề | Sai file hoặc sai âm thanh | kiểm tra file đề, chạy lại mục 4.2 (hoặc 4.10) |
| Máy ngủ khi gập nắp | Cài đặt gập nắp chưa được chặn | dùng `--lock` ở mục 4.10, chạy `bash ~/.cache/orchestrate_lid_restore.sh` nếu cần |
| CI đỏ ở bước `ruff format` | Code mới chưa chuẩn | `make fmt` rồi commit |
| CI đỏ sau khi thêm tính năng | Test giả định thứ tự tính năng | báo tôi, không tự sửa test của template |
| PR đỏ sau khi `main` thay đổi | Nhánh lạc hậu | cập nhật nhánh (mục 6), không bấm "Re-run" |
| `git push` bị từ chối | Có người push trước | `git pull --rebase origin main` rồi push lại, **không** force-push |
| Xung đột khi merge | Hai người sửa cùng file | dừng lại, báo tôi; đừng tự giải quyết |
| PR do bot (Copilot) tự mở | Bot sửa CI tự động | đóng PR đó, không merge |
| Agent sửa file ngoài phạm vi việc | Lời nhắc chưa chặt | `git checkout -- <file>`, nhắc lại "chỉ sửa các file: ..." |
| Demo hiện kết quả mẫu thay vì model thật | Cache chứa kết quả của provider `fake` | Bấm **Clear saved results**, làm nóng lại bằng `groq` (mục 7) |
| Demo mode báo `no cached result` | Input chưa được làm nóng | tắt Demo mode, chạy input đó với `groq` một lần, bật lại |
| `orchestrate.sh`: `.env holds filled-in keys` | `.env` có khóa lúc chạy | đặt lại `GROQ_API_KEY=` (để trống), chạy lại, điền khóa ở mục 4.11 |
| `STATUS.md`: Secret scan `ALERT` | Agent chép khóa vào tài liệu | **không** merge: `git worktree remove --force ../AI_FOR_GOOD-agent && git branch -D agent/plan`; thu hồi khóa trong console; bỏ khóa khỏi `.env` rồi chạy lại |
| Lỡ làm lộ khóa API | Dán nhầm vào chat/commit | thu hồi khóa trong console Groq ngay, tạo khóa mới |

## 9. Nhật ký (điền giờ thật, dùng cho lần sau)

| Mốc | Giờ |
|---|---|
| Bắt đầu ghi âm | |
| Tạo xong repo, mời 2 bạn | |
| `orchestrate.sh` khởi chạy | |
| Quay lại, đọc xong kế hoạch | |
| Chốt plan, `make lanes` lần đầu | |
| PR đầu tiên được merge | |
| Đóng băng | |
| Nộp Devpost | |

Bài học trong ngày (viết vào đây, sau cuộc thi đưa vào template):
-
