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
| Challenge của đội | **NOCO** (đã chốt). Đề: `docs/NOCO_Challenge_Statement.txt`. Bảng tính mẫu + rubric chấm: `docs/NOCO_Calculator_and_Judging_Rubric.txt` |
| **Tôi** | `Nguyen-Le-Tuan`: điều phối, quyết định, review và merge PR, thuyết trình |
| **Anh-08** | dùng **Claude Code** (vai trò `claude`): khung hợp đồng **T1**, dữ liệu GIS **T3**, bộ dữ liệu Buffalo **T7**, báo cáo xuất file **T10**, review máy tính **R1** |
| **phamvotriduc241106** | dùng **Codex**, **coder chính** (vai trò `codex`): máy tính **T2**, bản đồ Buffalo **T4**, khách tiềm năng **T5**, AI trích xuất **T11** (nếu kịp) |
| **NguyenQBao** | **làm slide/pitch** (T8), **hỏi người của NOCO và nghiên cứu dữ liệu** (T6), **QA và chạy demo** (T9), **người merge dự phòng**. Không viết code |

Hai agent viết code song song: **Anh-08 (Claude)** và **phamvotriduc241106 (Codex)**. Bạn (`Nguyen-Le-Tuan`) **kiểm tra PR, merge vào `main`, kiểm soát luồng việc**.
Mục **5** là bảng điều phối (tự sinh); **mục 6** là cách bạn vận hành và danh sách kiểm tra khi review PR. Đổi ai làm gì: sửa bảng **Team** trong
`docs/TASKS.md`, rồi `make lanes`.

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
3) Đăng nhập agent: Anh-08 chạy `claude`; phamvotriduc241106 chạy `codex`; NguyenQBao làm slide (không cần agent).
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
cd ~/Desktop/AI_FOR_GOOD && ./scripts/orchestrate.sh --check --transcript docs/NOCO_Challenge_Statement.txt
```
- [ ] Phải thấy `OK: ... .env holds no filled-in secret values`, `OK: Claude`, `OK: fallback claude-opus-5-5`, `OK: Codex`.
      Có `WARN` hoặc lỗi thì sửa theo mục 8 **trước khi** đi tiếp.

## 4. Luồng đề giấy: từ lúc có đề đến khi khóa hợp đồng

**4.1 Chuẩn bị file đề.**
- [ ] File chữ nằm ở `docs/NOCO_Challenge_Statement.txt`: `ls -la ~/Desktop/AI_FOR_GOOD/docs/NOCO_Challenge_Statement.txt`.
- [ ] **phamvotriduc241106 đối chiếu file chữ với đề giấy** (hạn chót, tỷ lệ/điểm, tên, số liệu, điều kiện bắt buộc,
      điểm cộng). File này do AI chép từ ảnh nên có thể sai hoặc thiếu. Gửi danh sách chỗ sai cho tôi. Có chỗ quan
      trọng thì sửa file chữ rồi chạy lại 4.2 (khoảng 5 phút).

**4.2 Chạy phân tích đề ngay** (không cần ghi âm, không cần khóa màn hình):
```bash
cd ~/Desktop/AI_FOR_GOOD && ./scripts/orchestrate.sh --now --transcript docs/NOCO_Challenge_Statement.txt --document --no-lid-guard
```
- Mất khoảng 5 phút: đọc đề, phê bình, lập kế hoạch cho từng challenge, rà soát kế hoạch. Có thử lại và dự phòng Opus.
- Muốn xem tiến độ: `cat ~/Desktop/AI_FOR_GOOD-agent/docs/agent/STATUS.md`. Dừng khẩn: `touch ~/Desktop/AI_FOR_GOOD/STOP`.
- [ ] Đã chạy lúc: ______

**4.3 Trong 5 phút chờ, cả bốn người làm song song.**
- [ ] **Tôi:** đọc đề NOCO và bảng tính mẫu, ghi câu hỏi cần hỏi người của NOCO.
- [ ] **phamvotriduc241106:** làm 4.1, rồi đi hỏi ban tổ chức/đối tác (gửi tin dưới) và xác nhận đội ở bàn tiếp tân.
- [ ] **Anh-08 và NguyenQBao:** đọc đề NOCO và bảng tính mẫu, ghi 2 dòng: phần nào làm bằng quy tắc thường, phần nào cần AI.
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
- [ ] `BRIEF.md` khớp đề NOCO và rubric: câu hỏi chính, các mục phải tính, điểm cộng. Đối chiếu số liệu với file đề.
- [ ] Ghi lại mục "Uncertain or missing" của BRIEF để hỏi ban tổ chức.

**4.5 Chọn challenge và plan (khoảng 10 phút, cả bốn người cùng quyết, sau khi có câu trả lời ở 4.3).**
- [ ] Tiêu chí: (1) khớp tiêu chí chấm, (2) **một** người dùng, một đường demo rõ, (3) dùng dữ liệu/API công khai hoặc
      của đối tác nếu được phép, (4) làm trọn trong thời gian còn lại, (5) demo ổn định.
- [ ] Challenge và plan đã chọn: ______ (ghi vào đây)
- [ ] Đưa tài liệu kế hoạch vào `main`: `cd ~/Desktop/AI_FOR_GOOD && git switch main && git merge agent/plan`

**4.6 Soạn `docs/spec.md` (tôi duyệt từng dòng).** Mở Claude Code trong repo (`claude`) rồi dán, thay `X` bằng
challenge/plan đã chọn:
```text
Đọc docs/agent/BRIEF.md, docs/agent/PLAN_REVIEW.md, docs/agent/PLANS.md và docs/NOCO_Challenge_Statement.txt.
Challenge của đội là NOCO (đã chốt); hướng đi và phạm vi là hướng GIS + dữ liệu tài sản công khai đã duyệt trong docs/spec.md. Soạn docs/spec.md theo đúng 6 mục của file mẫu, thêm
câu trả lời của đối tác dưới đây (kể cả việc dữ liệu có được gửi sang dịch vụ AI không): <dán câu trả lời>.
Chỉ ghi điều có trong tài liệu hoặc câu trả lời, ghi rõ chỗ chưa chắc. Không viết code.
```
- [ ] Đã đọc và sửa `docs/spec.md` (vấn đề, **một** người dùng, đường demo từng bước, ngoài phạm vi).

**4.7 Điền `AGENTS.md` (khối Project) và `docs/TASKS.md` (khóa hợp đồng).** Vẫn trong Claude Code:
```text
Từ docs/spec.md: (1) điền khối "Project (FILL ON EVENT DAY)" trong AGENTS.md; (2) điền docs/TASKS.md:
Contract (feature key, schema, rules, file mẫu, eval) và bảng Tasks theo bốn việc của kế hoạch đã chọn trong
PLAN_REVIEW. Giữ nguyên bảng Team (bốn người; hai agent viết code: claude = Anh-08, codex = phamvotriduc241106;
NguyenQBao làm slide, QA, nghiên cứu). Quy ước: T1 là khung đăng ký tính năng, merge trong ~10 phút;
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
cd ~/Desktop/AI_FOR_GOOD && ./scripts/orchestrate.sh --now --lecturebridge --with-file docs/NOCO_Challenge_Statement.txt --with-file docs/NOCO_Calculator_and_Judging_Rubric.txt --chosen "NOCO: address-to-quote insulation savings tool with GIS and public property data" --no-lid-guard
```
   Muốn hẹn giờ và khóa màn hình để rời đi:
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
> Tự sinh bởi `make lanes` lúc 2026-10-03 12:18 từ `docs/TASKS.md`. **Đừng sửa tay trong khối này**: sửa `docs/TASKS.md` (cột Status, Owner) rồi chạy lại.

### Đội hình và việc được giao

| Người | Công cụ | Vai trò: việc |
|---|---|---|
| Anh-08 | Claude Code | claude (agent): T1, T3, T7, T10, R1 |
| phamvotriduc241106 | Codex | codex (agent): T2, T4, T5, T11 |
| Nguyen-Le-Tuan (tôi) | — | human-a (điều phối, review và merge PR): — |
| NguyenQBao | — | human-b (QA, chạy demo): T9; human-c (pitch, Devpost): T8; partner-qa (hỏi đối tác): —; researcher (tìm dữ liệu công khai): T6; backup-integrator (merge dự phòng): — |

### Ngay bây giờ

**▶ SẴN SÀNG làm ngay (chạy song song được)**
- `T1` [MUST] Khung hợp đồng: contract.py, fixtures.py (ví dụ NOCO + 5 tòa nhà giả có đa giác), __init__.py đăng ký feature noco_scout. Mở PR trong ~15 phút — Anh-08 (Claude Code)
- `T2` [MUST] Máy tính: estimate_insulation, inputs_from_facts; test Golden với ví dụ NOCO (dung sai 0,1%) và các ca biên (thiếu chi phí, tiết kiệm bằng 0, R không hợp lệ) — phamvotriduc241106 (Codex) — làm được ngay, chỉ HOÀN TẤT sau khi T1 merge
- `T3` [MUST] Bộ nối dữ liệu GIS: geocode, fetch_footprint, fetch_property, build_facts, bộ nhớ đệm; test chỉ dùng phản hồi đã ghi — Anh-08 (Claude Code) — làm được ngay, chỉ HOÀN TẤT sau khi T1 merge
- `T4` [MUST] Bản đồ Buffalo 3D và các trang: tooltip nguồn khi rê chuột, bấm ra bảng chi tiết, trang "Address to Quote", nút "Show potential customers" và bộ lọc, chế độ offline. Làm trên fixtures.py trước, nối T2/T3/T5/T7 khi chúng merge — phamvotriduc241106 (Codex) — làm được ngay, chỉ HOÀN TẤT sau khi T1 merge
- `T6` [MUST] Nghiên cứu và hỏi NOCO: xác nhận hằng số (HDD, CDD, hệ số làm mát), ưu đãi, chi phí cách nhiệt/sq ft, biên lợi nhuận, "provider" nghĩa là gì, câu hỏi chu vi; lấy gói tài liệu NOCO ở cuối phòng; ghi nguồn, giấy phép, kịch bản chi phí vào docs/DATA.md — NguyenQBao
- `T8` [MUST] Pitch: kịch bản 4 phút, slide PDF/PowerPoint ánh xạ rubric, kịch bản demo, video dự phòng — NguyenQBao

**⏳ ĐANG CHỜ**
- `T5` [SHOULD] Khách tiềm năng: build_opportunity (utility, ưu đãi, doanh thu và lợi nhuận minh họa) và rank_prospects — phamvotriduc241106 (Codex) — chờ T2 (phamvotriduc241106 (Codex))
- `T7` [MUST ≥40 tòa, SHOULD 150-300] Lấy trước bộ dữ liệu Buffalo (Downtown, Allentown, Elmwood): đa giác, tầng, loại tài sản, độ chắc chắn của phép nối OSM <-> bảng Buffalo, vào data/public/demo_buildings.json, script chạy lại được — Anh-08 (Claude Code) — chờ T3 (Anh-08 (Claude Code))
- `T10` [MUST báo cáo khách, SHOULD báo cáo sếp + CSV] Xuất báo cáo: render_customer_report, render_manager_report, prospects_to_csv (HTML in được, không thêm thư viện) — Anh-08 (Claude Code) — chờ T2 (phamvotriduc241106 (Codex))
- `T11` [COULD] AI trích xuất ghi chú hiện trường/hóa đơn giả thành SiteNote, 3 ca eval với fake_response — phamvotriduc241106 (Codex) — chờ T2 (phamvotriduc241106 (Codex))
- `T9` [MUST] QA: chạy toàn luồng offline, kiểm tra quy tắc dữ liệu (không có chủ sở hữu, có ghi nguồn OSM, nhãn ILLUSTRATIVE), tập demo 3 lần, make test && make lint — NguyenQBao — chờ T4 (phamvotriduc241106 (Codex)), T5 (phamvotriduc241106 (Codex)), T7 (Anh-08 (Claude Code)), T10 (Anh-08 (Claude Code))
- `R1` Review T2 so với công thức trong spec và các con số Golden. Chỉ báo cáo, không sửa — Anh-08 (Claude Code) — chờ T2 (phamvotriduc241106 (Codex))

### Các đợt (thứ tự tối ưu, tính từ phụ thuộc)

**Đợt 1** (chạy song song)
- `T1` [MUST] Khung hợp đồng: contract.py, fixtures.py (ví dụ NOCO + 5 tòa nhà giả có đa giác), __init__.py đăng ký feature noco_scout. Mở PR trong ~15 phút — Anh-08 (Claude Code)
- `T2` [MUST] Máy tính: estimate_insulation, inputs_from_facts; test Golden với ví dụ NOCO (dung sai 0,1%) và các ca biên (thiếu chi phí, tiết kiệm bằng 0, R không hợp lệ) — phamvotriduc241106 (Codex)
- `T3` [MUST] Bộ nối dữ liệu GIS: geocode, fetch_footprint, fetch_property, build_facts, bộ nhớ đệm; test chỉ dùng phản hồi đã ghi — Anh-08 (Claude Code)
- `T4` [MUST] Bản đồ Buffalo 3D và các trang: tooltip nguồn khi rê chuột, bấm ra bảng chi tiết, trang "Address to Quote", nút "Show potential customers" và bộ lọc, chế độ offline. Làm trên fixtures.py trước, nối T2/T3/T5/T7 khi chúng merge — phamvotriduc241106 (Codex)
- `T6` [MUST] Nghiên cứu và hỏi NOCO: xác nhận hằng số (HDD, CDD, hệ số làm mát), ưu đãi, chi phí cách nhiệt/sq ft, biên lợi nhuận, "provider" nghĩa là gì, câu hỏi chu vi; lấy gói tài liệu NOCO ở cuối phòng; ghi nguồn, giấy phép, kịch bản chi phí vào docs/DATA.md — NguyenQBao
- `T8` [MUST] Pitch: kịch bản 4 phút, slide PDF/PowerPoint ánh xạ rubric, kịch bản demo, video dự phòng — NguyenQBao

**Đợt 2** (chạy song song)
- `T5` [SHOULD] Khách tiềm năng: build_opportunity (utility, ưu đãi, doanh thu và lợi nhuận minh họa) và rank_prospects — phamvotriduc241106 (Codex)
- `T7` [MUST ≥40 tòa, SHOULD 150-300] Lấy trước bộ dữ liệu Buffalo (Downtown, Allentown, Elmwood): đa giác, tầng, loại tài sản, độ chắc chắn của phép nối OSM <-> bảng Buffalo, vào data/public/demo_buildings.json, script chạy lại được — Anh-08 (Claude Code)
- `T10` [MUST báo cáo khách, SHOULD báo cáo sếp + CSV] Xuất báo cáo: render_customer_report, render_manager_report, prospects_to_csv (HTML in được, không thêm thư viện) — Anh-08 (Claude Code)
- `T11` [COULD] AI trích xuất ghi chú hiện trường/hóa đơn giả thành SiteNote, 3 ca eval với fake_response — phamvotriduc241106 (Codex)
- `R1` Review T2 so với công thức trong spec và các con số Golden. Chỉ báo cáo, không sửa — Anh-08 (Claude Code)

**Đợt 3**
- `T9` [MUST] QA: chạy toàn luồng offline, kiểm tra quy tắc dữ liệu (không có chủ sở hữu, có ghi nguồn OSM, nhãn ILLUSTRATIVE), tập demo 3 lần, make test && make lint — NguyenQBao

### Bảng chi tiết

| ID | Việc | Người | Nhánh | Chờ | Trạng thái |
|---|---|---|---|---|---|
| T1 | [MUST] Khung hợp đồng: contract.py, fixtures.py (ví dụ NOCO + 5 tòa nhà giả có đa giác), __init__.py đăng ký feature noco_scout. Mở PR trong ~15 phút | Anh-08 | `task/t1` | — | todo |
| T2 | [MUST] Máy tính: estimate_insulation, inputs_from_facts; test Golden với ví dụ NOCO (dung sai 0,1%) và các ca biên (thiếu chi phí, tiết kiệm bằng 0, R không hợp lệ) | phamvotriduc241106 | `task/t2` | T1~ (Anh-08, chỉ để hoàn tất) | todo |
| T3 | [MUST] Bộ nối dữ liệu GIS: geocode, fetch_footprint, fetch_property, build_facts, bộ nhớ đệm; test chỉ dùng phản hồi đã ghi | Anh-08 | `task/t3` | T1~ (Anh-08, chỉ để hoàn tất) | todo |
| T4 | [MUST] Bản đồ Buffalo 3D và các trang: tooltip nguồn khi rê chuột, bấm ra bảng chi tiết, trang "Address to Quote", nút "Show potential customers" và bộ lọc, chế độ offline. Làm trên fixtures.py trước, nối T2/T3/T5/T7 khi chúng merge | phamvotriduc241106 | `task/t4` | T1~ (Anh-08, chỉ để hoàn tất) | todo |
| T5 | [SHOULD] Khách tiềm năng: build_opportunity (utility, ưu đãi, doanh thu và lợi nhuận minh họa) và rank_prospects | phamvotriduc241106 | `task/t5` | T2 (phamvotriduc241106) | todo |
| T6 | [MUST] Nghiên cứu và hỏi NOCO: xác nhận hằng số (HDD, CDD, hệ số làm mát), ưu đãi, chi phí cách nhiệt/sq ft, biên lợi nhuận, "provider" nghĩa là gì, câu hỏi chu vi; lấy gói tài liệu NOCO ở cuối phòng; ghi nguồn, giấy phép, kịch bản chi phí vào docs/DATA.md | NguyenQBao | `task/t6` | — | todo |
| T7 | [MUST ≥40 tòa, SHOULD 150-300] Lấy trước bộ dữ liệu Buffalo (Downtown, Allentown, Elmwood): đa giác, tầng, loại tài sản, độ chắc chắn của phép nối OSM <-> bảng Buffalo, vào data/public/demo_buildings.json, script chạy lại được | Anh-08 | `task/t7` | T3 (Anh-08) | todo |
| T8 | [MUST] Pitch: kịch bản 4 phút, slide PDF/PowerPoint ánh xạ rubric, kịch bản demo, video dự phòng | NguyenQBao | `task/t8` | — | todo |
| T10 | [MUST báo cáo khách, SHOULD báo cáo sếp + CSV] Xuất báo cáo: render_customer_report, render_manager_report, prospects_to_csv (HTML in được, không thêm thư viện) | Anh-08 | `task/t10` | T2 (phamvotriduc241106) | todo |
| T11 | [COULD] AI trích xuất ghi chú hiện trường/hóa đơn giả thành SiteNote, 3 ca eval với fake_response | phamvotriduc241106 | `task/t11` | T2 (phamvotriduc241106) | todo |
| T9 | [MUST] QA: chạy toàn luồng offline, kiểm tra quy tắc dữ liệu (không có chủ sở hữu, có ghi nguồn OSM, nhãn ILLUSTRATIVE), tập demo 3 lần, make test && make lint | NguyenQBao | `task/t9` | T4 (phamvotriduc241106), T5 (phamvotriduc241106), T7 (Anh-08), T10 (Anh-08) | todo |
| R1 | Review T2 so với công thức trong spec và các con số Golden. Chỉ báo cáo, không sửa | Anh-08 | (không cần, chỉ đọc) | T2 (phamvotriduc241106) | todo |
### Tin nhắn cho nhóm chat (copy)

```text
LÀM NGAY:
@Anh-08 -> T1: [MUST] Khung hợp đồng: contract.py, fixtures.py (ví dụ NOCO + 5 tòa nhà giả có đa giác), __init__.py đăng ký feature noco_scout. Mở PR trong ~15 phút
@phamvotriduc241106 -> T2: [MUST] Máy tính: estimate_insulation, inputs_from_facts; test Golden với ví dụ NOCO (dung sai 0,1%) và các ca biên (thiếu chi phí, tiết kiệm bằng 0, R không hợp lệ)
@Anh-08 -> T3: [MUST] Bộ nối dữ liệu GIS: geocode, fetch_footprint, fetch_property, build_facts, bộ nhớ đệm; test chỉ dùng phản hồi đã ghi
@phamvotriduc241106 -> T4: [MUST] Bản đồ Buffalo 3D và các trang: tooltip nguồn khi rê chuột, bấm ra bảng chi tiết, trang "Address to Quote", nút "Show potential customers" và bộ lọc, chế độ offline. Làm trên fixtures.py trước, nối T2/T3/T5/T7 khi chúng merge
@NguyenQBao -> T6: [MUST] Nghiên cứu và hỏi NOCO: xác nhận hằng số (HDD, CDD, hệ số làm mát), ưu đãi, chi phí cách nhiệt/sq ft, biên lợi nhuận, "provider" nghĩa là gì, câu hỏi chu vi; lấy gói tài liệu NOCO ở cuối phòng; ghi nguồn, giấy phép, kịch bản chi phí vào docs/DATA.md
@NguyenQBao -> T8: [MUST] Pitch: kịch bản 4 phút, slide PDF/PowerPoint ánh xạ rubric, kịch bản demo, video dự phòng
CHUẨN BỊ, CHỜ TÔI BÁO:
@phamvotriduc241106 -> T5: [SHOULD] Khách tiềm năng: build_opportunity (utility, ưu đãi, doanh thu và lợi nhuận minh họa) và rank_prospects
@Anh-08 -> T7: [MUST ≥40 tòa, SHOULD 150-300] Lấy trước bộ dữ liệu Buffalo (Downtown, Allentown, Elmwood): đa giác, tầng, loại tài sản, độ chắc chắn của phép nối OSM <-> bảng Buffalo, vào data/public/demo_buildings.json, script chạy lại được
@Anh-08 -> T10: [MUST báo cáo khách, SHOULD báo cáo sếp + CSV] Xuất báo cáo: render_customer_report, render_manager_report, prospects_to_csv (HTML in được, không thêm thư viện)
@phamvotriduc241106 -> T11: [COULD] AI trích xuất ghi chú hiện trường/hóa đơn giả thành SiteNote, 3 ca eval với fake_response
@NguyenQBao -> T9: [MUST] QA: chạy toàn luồng offline, kiểm tra quy tắc dữ liệu (không có chủ sở hữu, có ghi nguồn OSM, nhãn ILLUSTRATIVE), tập demo 3 lần, make test && make lint
@Anh-08 -> R1: Review T2 so với công thức trong spec và các con số Golden. Chỉ báo cáo, không sửa
```

### Lệnh cho từng người (copy–paste)

#### Anh-08

**T1: [MUST] Khung hợp đồng: contract.py, fixtures.py (ví dụ NOCO + 5 tòa nhà giả có đa giác), __init__.py đăng ký feature noco_scout. Mở PR trong ~15 phút** — _sẵn sàng_

```bash
cd AI_FOR_GOOD   # thư mục repo bạn đã clone
git switch main && git pull origin main
git switch -c task/t1
claude
```
Lời nhắc cho agent:
```text
Đọc AGENTS.md, docs/spec.md và docs/TASKS.md. Chỉ làm task T1: [MUST] Khung hợp đồng: contract.py, fixtures.py (ví dụ NOCO + 5 tòa nhà giả có đa giác), __init__.py đăng ký feature noco_scout. Mở PR trong ~15 phút. Chỉ sửa các file: src/features/noco_scout/contract.py, src/features/noco_scout/fixtures.py, src/features/noco_scout/__init__.py. Tuân thủ đúng phần Contract trong docs/TASKS.md. Chạy pytest và ruff check . rồi commit nhỏ; xong thì dừng và báo kết quả. Không merge, không push lên main.
```
Khi agent báo xong:
```bash
make test && make lint
git push -u origin task/t1
gh pr create --base main --fill
```
Rồi nhắn cho tôi số PR.

**T3: [MUST] Bộ nối dữ liệu GIS: geocode, fetch_footprint, fetch_property, build_facts, bộ nhớ đệm; test chỉ dùng phản hồi đã ghi** — _sẵn sàng_

```bash
cd AI_FOR_GOOD   # thư mục repo bạn đã clone
git switch main && git pull origin main
git switch -c task/t3
claude
```
Lời nhắc cho agent:
```text
Đọc AGENTS.md, docs/spec.md và docs/TASKS.md. Chỉ làm task T3: [MUST] Bộ nối dữ liệu GIS: geocode, fetch_footprint, fetch_property, build_facts, bộ nhớ đệm; test chỉ dùng phản hồi đã ghi. Chỉ sửa các file: src/features/noco_scout/geo.py, tests/test_noco_geo.py, tests/fixtures/noco/, .gitignore, data/public/cache/. Tuân thủ đúng phần Contract trong docs/TASKS.md. Task này chỉ phụ thuộc mềm vào T1: bắt đầu ngay được, nhưng chỉ chạy eval và hoàn tất sau khi T1 đã merge vào main (khi đó chạy `git fetch origin && git merge origin/main`). Chạy pytest và ruff check . rồi commit nhỏ; xong thì dừng và báo kết quả. Không merge, không push lên main.
```
Khi agent báo xong:
```bash
make test && make lint
git push -u origin task/t3
gh pr create --base main --fill
```
Rồi nhắn cho tôi số PR.

**T7: [MUST ≥40 tòa, SHOULD 150-300] Lấy trước bộ dữ liệu Buffalo (Downtown, Allentown, Elmwood): đa giác, tầng, loại tài sản, độ chắc chắn của phép nối OSM <-> bảng Buffalo, vào data/public/demo_buildings.json, script chạy lại được** — _đang chờ_

⏳ CHƯA chạy các lệnh dưới. Chờ T3 xong, tôi sẽ báo.

```bash
cd AI_FOR_GOOD   # thư mục repo bạn đã clone
git switch main && git pull origin main
git switch -c task/t7
claude
```
Lời nhắc cho agent:
```text
Đọc AGENTS.md, docs/spec.md và docs/TASKS.md. Chỉ làm task T7: [MUST ≥40 tòa, SHOULD 150-300] Lấy trước bộ dữ liệu Buffalo (Downtown, Allentown, Elmwood): đa giác, tầng, loại tài sản, độ chắc chắn của phép nối OSM <-> bảng Buffalo, vào data/public/demo_buildings.json, script chạy lại được. Chỉ sửa các file: scripts/prefetch_noco_data.py, data/public/. Tuân thủ đúng phần Contract trong docs/TASKS.md. Chạy pytest và ruff check . rồi commit nhỏ; xong thì dừng và báo kết quả. Không merge, không push lên main.
```
Khi agent báo xong:
```bash
make test && make lint
git push -u origin task/t7
gh pr create --base main --fill
```
Rồi nhắn cho tôi số PR.

**T10: [MUST báo cáo khách, SHOULD báo cáo sếp + CSV] Xuất báo cáo: render_customer_report, render_manager_report, prospects_to_csv (HTML in được, không thêm thư viện)** — _đang chờ_

⏳ CHƯA chạy các lệnh dưới. Chờ T2 xong, tôi sẽ báo.

```bash
cd AI_FOR_GOOD   # thư mục repo bạn đã clone
git switch main && git pull origin main
git switch -c task/t10
claude
```
Lời nhắc cho agent:
```text
Đọc AGENTS.md, docs/spec.md và docs/TASKS.md. Chỉ làm task T10: [MUST báo cáo khách, SHOULD báo cáo sếp + CSV] Xuất báo cáo: render_customer_report, render_manager_report, prospects_to_csv (HTML in được, không thêm thư viện). Chỉ sửa các file: src/features/noco_scout/report.py, tests/test_noco_report.py. Tuân thủ đúng phần Contract trong docs/TASKS.md. Chạy pytest và ruff check . rồi commit nhỏ; xong thì dừng và báo kết quả. Không merge, không push lên main.
```
Khi agent báo xong:
```bash
make test && make lint
git push -u origin task/t10
gh pr create --base main --fill
```
Rồi nhắn cho tôi số PR.

**R1: Review T2 so với công thức trong spec và các con số Golden. Chỉ báo cáo, không sửa** — _đang chờ_

⏳ CHƯA chạy các lệnh dưới. Chờ T2 xong, tôi sẽ báo.

```bash
git fetch origin
git diff origin/main...origin/task/t2 | less
claude
```
Lời nhắc cho agent:
```text
Review nhánh origin/task/t2 so với main (git diff origin/main...origin/task/t2). Đối chiếu với phần Contract trong docs/TASKS.md. Chỉ báo cáo lỗi và rủi ro theo mức độ, không sửa file nào.
```

#### phamvotriduc241106

**T2: [MUST] Máy tính: estimate_insulation, inputs_from_facts; test Golden với ví dụ NOCO (dung sai 0,1%) và các ca biên (thiếu chi phí, tiết kiệm bằng 0, R không hợp lệ)** — _sẵn sàng_

```bash
cd AI_FOR_GOOD   # thư mục repo bạn đã clone
git switch main && git pull origin main
git switch -c task/t2
codex
```
Lời nhắc cho agent:
```text
Đọc AGENTS.md, docs/spec.md và docs/TASKS.md. Chỉ làm task T2: [MUST] Máy tính: estimate_insulation, inputs_from_facts; test Golden với ví dụ NOCO (dung sai 0,1%) và các ca biên (thiếu chi phí, tiết kiệm bằng 0, R không hợp lệ). Chỉ sửa các file: src/features/noco_scout/calc.py, tests/test_noco_calc.py. Tuân thủ đúng phần Contract trong docs/TASKS.md. Task này chỉ phụ thuộc mềm vào T1: bắt đầu ngay được, nhưng chỉ chạy eval và hoàn tất sau khi T1 đã merge vào main (khi đó chạy `git fetch origin && git merge origin/main`). Chạy pytest và ruff check . rồi commit nhỏ; xong thì dừng và báo kết quả. Không merge, không push lên main.
```
Khi agent báo xong:
```bash
make test && make lint
git push -u origin task/t2
gh pr create --base main --fill
```
Rồi nhắn cho tôi số PR.

**T4: [MUST] Bản đồ Buffalo 3D và các trang: tooltip nguồn khi rê chuột, bấm ra bảng chi tiết, trang "Address to Quote", nút "Show potential customers" và bộ lọc, chế độ offline. Làm trên fixtures.py trước, nối T2/T3/T5/T7 khi chúng merge** — _sẵn sàng_

```bash
cd AI_FOR_GOOD   # thư mục repo bạn đã clone
git switch main && git pull origin main
git switch -c task/t4
codex
```
Lời nhắc cho agent:
```text
Đọc AGENTS.md, docs/spec.md và docs/TASKS.md. Chỉ làm task T4: [MUST] Bản đồ Buffalo 3D và các trang: tooltip nguồn khi rê chuột, bấm ra bảng chi tiết, trang "Address to Quote", nút "Show potential customers" và bộ lọc, chế độ offline. Làm trên fixtures.py trước, nối T2/T3/T5/T7 khi chúng merge. Chỉ sửa các file: src/features/noco_scout/mapdata.py, app/pages/, tests/test_noco_mapdata.py. Tuân thủ đúng phần Contract trong docs/TASKS.md. Task này chỉ phụ thuộc mềm vào T1: bắt đầu ngay được, nhưng chỉ chạy eval và hoàn tất sau khi T1 đã merge vào main (khi đó chạy `git fetch origin && git merge origin/main`). Chạy pytest và ruff check . rồi commit nhỏ; xong thì dừng và báo kết quả. Không merge, không push lên main.
```
Khi agent báo xong:
```bash
make test && make lint
git push -u origin task/t4
gh pr create --base main --fill
```
Rồi nhắn cho tôi số PR.

**T5: [SHOULD] Khách tiềm năng: build_opportunity (utility, ưu đãi, doanh thu và lợi nhuận minh họa) và rank_prospects** — _đang chờ_

⏳ CHƯA chạy các lệnh dưới. Chờ T2 xong, tôi sẽ báo.

```bash
cd AI_FOR_GOOD   # thư mục repo bạn đã clone
git switch main && git pull origin main
git switch -c task/t5
codex
```
Lời nhắc cho agent:
```text
Đọc AGENTS.md, docs/spec.md và docs/TASKS.md. Chỉ làm task T5: [SHOULD] Khách tiềm năng: build_opportunity (utility, ưu đãi, doanh thu và lợi nhuận minh họa) và rank_prospects. Chỉ sửa các file: src/features/noco_scout/prospect.py, tests/test_noco_prospect.py. Tuân thủ đúng phần Contract trong docs/TASKS.md. Chạy pytest và ruff check . rồi commit nhỏ; xong thì dừng và báo kết quả. Không merge, không push lên main.
```
Khi agent báo xong:
```bash
make test && make lint
git push -u origin task/t5
gh pr create --base main --fill
```
Rồi nhắn cho tôi số PR.

**T11: [COULD] AI trích xuất ghi chú hiện trường/hóa đơn giả thành SiteNote, 3 ca eval với fake_response** — _đang chờ_

⏳ CHƯA chạy các lệnh dưới. Chờ T2 xong, tôi sẽ báo.

```bash
cd AI_FOR_GOOD   # thư mục repo bạn đã clone
git switch main && git pull origin main
git switch -c task/t11
codex
```
Lời nhắc cho agent:
```text
Đọc AGENTS.md, docs/spec.md và docs/TASKS.md. Chỉ làm task T11: [COULD] AI trích xuất ghi chú hiện trường/hóa đơn giả thành SiteNote, 3 ca eval với fake_response. Chỉ sửa các file: src/features/noco_scout/__init__.py, evals/cases/noco_scout.jsonl, data/synthetic/site_notes/, tests/test_noco_extract.py. Tuân thủ đúng phần Contract trong docs/TASKS.md. Chạy pytest và ruff check . rồi commit nhỏ; xong thì dừng và báo kết quả. Không merge, không push lên main.
```
Khi agent báo xong:
```bash
make test && make lint
git push -u origin task/t11
gh pr create --base main --fill
```
Rồi nhắn cho tôi số PR.

#### NguyenQBao

**T6: [MUST] Nghiên cứu và hỏi NOCO: xác nhận hằng số (HDD, CDD, hệ số làm mát), ưu đãi, chi phí cách nhiệt/sq ft, biên lợi nhuận, "provider" nghĩa là gì, câu hỏi chu vi; lấy gói tài liệu NOCO ở cuối phòng; ghi nguồn, giấy phép, kịch bản chi phí vào docs/DATA.md** — _sẵn sàng_

```bash
cd AI_FOR_GOOD   # thư mục repo bạn đã clone
git switch main && git pull origin main
make test && make lint && make demo   # kiểm tra nhanh trước khi làm
```
Việc thủ công: [MUST] Nghiên cứu và hỏi NOCO: xác nhận hằng số (HDD, CDD, hệ số làm mát), ưu đãi, chi phí cách nhiệt/sq ft, biên lợi nhuận, "provider" nghĩa là gì, câu hỏi chu vi; lấy gói tài liệu NOCO ở cuối phòng; ghi nguồn, giấy phép, kịch bản chi phí vào docs/DATA.md. File được sửa: docs/DATA.md, docs/T6_NOCO_questions.txt.
Nếu việc này có sửa file, làm trên nhánh riêng rồi mở PR:
```bash
git switch -c task/t6
# ...làm việc, có thể mở claude hoặc codex để hỗ trợ...
git add -A && git commit -m "T6: cập nhật" && git push -u origin task/t6
gh pr create --base main --fill
```

**T8: [MUST] Pitch: kịch bản 4 phút, slide PDF/PowerPoint ánh xạ rubric, kịch bản demo, video dự phòng** — _sẵn sàng_

```bash
cd AI_FOR_GOOD   # thư mục repo bạn đã clone
git switch main && git pull origin main
make test && make lint && make demo   # kiểm tra nhanh trước khi làm
```
Việc thủ công: [MUST] Pitch: kịch bản 4 phút, slide PDF/PowerPoint ánh xạ rubric, kịch bản demo, video dự phòng. File được sửa: docs/PITCH.md, docs/pitch/, README.md.
Nếu việc này có sửa file, làm trên nhánh riêng rồi mở PR:
```bash
git switch -c task/t8
# ...làm việc, có thể mở claude hoặc codex để hỗ trợ...
git add -A && git commit -m "T8: cập nhật" && git push -u origin task/t8
gh pr create --base main --fill
```

**T9: [MUST] QA: chạy toàn luồng offline, kiểm tra quy tắc dữ liệu (không có chủ sở hữu, có ghi nguồn OSM, nhãn ILLUSTRATIVE), tập demo 3 lần, make test && make lint** — _đang chờ_

⏳ CHƯA chạy các lệnh dưới. Chờ T4, T5, T7, T10 xong, tôi sẽ báo.

```bash
cd AI_FOR_GOOD   # thư mục repo bạn đã clone
git switch main && git pull origin main
make test && make lint && make demo   # kiểm tra nhanh trước khi làm
```
Việc thủ công: [MUST] QA: chạy toàn luồng offline, kiểm tra quy tắc dữ liệu (không có chủ sở hữu, có ghi nguồn OSM, nhãn ILLUSTRATIVE), tập demo 3 lần, make test && make lint. File được sửa: app/.
Nếu việc này có sửa file, làm trên nhánh riêng rồi mở PR:
```bash
git switch -c task/t9
# ...làm việc, có thể mở claude hoặc codex để hỗ trợ...
git add -A && git commit -m "T9: cập nhật" && git push -u origin task/t9
gh pr create --base main --fill
```

#### Nguyen-Le-Tuan (tôi) (điều phối): mỗi khi có PR

```bash
gh pr list
gh pr checks <số PR> --watch        # chỉ merge khi xanh
gh pr merge <số PR> --merge
git switch main && git pull origin main && make test && make lint
```
PR bị lạc hậu so với main? `gh api -X PUT repos/Nguyen-Le-Tuan/AI_FOR_GOOD/pulls/<số PR>/update-branch`, hoặc người làm chạy `git fetch origin && git merge origin/main && git push`.

Người merge dự phòng khi tôi bận: NguyenQBao (chỉ merge PR xanh, không merge PR của chính mình).

**Sau khi merge một task, báo ngay cho người đang chờ:**
- merge `T1` → báo phamvotriduc241106 (T2), Anh-08 (T3), phamvotriduc241106 (T4): chạy `git fetch origin && git merge origin/main`
- merge `T2` → báo phamvotriduc241106 (T5), Anh-08 (T10), phamvotriduc241106 (T11), Anh-08 (R1): chạy `git fetch origin && git merge origin/main`
- merge `T3` → báo Anh-08 (T7): chạy `git fetch origin && git merge origin/main`
- merge `T4` → báo NguyenQBao (T9): chạy `git fetch origin && git merge origin/main`
- merge `T5` → báo NguyenQBao (T9): chạy `git fetch origin && git merge origin/main`
- merge `T7` → báo NguyenQBao (T9): chạy `git fetch origin && git merge origin/main`
- merge `T10` → báo NguyenQBao (T9): chạy `git fetch origin && git merge origin/main`

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
- **Người merge dự phòng: NguyenQBao** (không viết code nên không tự merge PR của mình). Khi tôi bận (hỏi đối tác, trình bày),
  NguyenQBao merge theo đúng quy trình trên. Chỉ merge PR **xanh** và nhắn tôi sau mỗi lần merge để tôi chạy `make lanes SET=...`.

**Danh sách kiểm tra khi review mỗi PR (tôi làm, mất ~2 phút, vì chỉ còn một review chéo bằng agent):**
- [ ] CI xanh (`gh pr checks <số PR> --watch`) và PR không chạm file ngoài cột "Files it may touch" của việc đó (`gh pr diff <số PR> --name-only`).
- [ ] Không có trường chủ sở hữu: `gh pr diff <số PR> | grep -iE "owner1|mail3|mail4|mail_zip"` phải **rỗng**.
- [ ] Test không gọi mạng: `gh pr diff <số PR> | grep -nE "requests\.|httpx\.|urlopen|overpass|census"` chỉ được thấy trong `geo.py` (và test dùng dữ liệu đã ghi).
- [ ] Tên hàm, kiểu dữ liệu đúng **Contract** trong `docs/TASKS.md` (không đổi chữ ký nếu chưa hỏi tôi).
- [ ] Mọi con số hiển thị ra người dùng có nguồn; lợi nhuận/doanh thu của NOCO có nhãn **ILLUSTRATIVE**; không đoán nhà cung cấp hiện tại.
- [ ] Không có khóa API: `python3 scripts/secret_scan.py --repo . --since origin/main`.
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
