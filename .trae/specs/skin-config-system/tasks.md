# Tasks

- [x] Task 1: 修改 skin_loader.py 支持 skin.yaml 配置
  - [x] SubTask 1.1: 添加 `_load_skin_config` 函数读取 skin.yaml
  - [x] SubTask 1.2: 修改 `find_template` 函数支持配置映射
  - [x] SubTask 1.3: 保持向后兼容（无配置时使用默认命名约定）

- [x] Task 2: 为 default skin 创建 skin.yaml 配置文件
  - [x] SubTask 2.1: 创建 `skins/default/skin.yaml`
  - [x] SubTask 2.2: 配置所有 renderer 到模板的映射

- [x] Task 3: 更新文档
  - [x] SubTask 3.1: 更新 `docs/skin_guide.md` 说明配置文件用法

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1, Task 2]
