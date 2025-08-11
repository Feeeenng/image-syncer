import yaml
import sys
from pathlib import Path

def generate_yaml(image_file: str, mode: str):
    if mode not in ["offline", "online"]:
        print("参数错误，只能是 offline 或 online")
        sys.exit(1)

    image_file_path = Path(image_file)
    if not image_file_path.exists():
        print(f"找不到镜像列表文件: {image_file}")
        sys.exit(1)

    output_dir = Path(mode)
    output_dir.mkdir(parents=True, exist_ok=True)

    tencent_images = {}
    other_images = {}

    with open(image_file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("docker pull"):
                continue

            parts = line.split()
            if len(parts) >= 3:
                image = parts[2]
            elif len(parts) == 2:
                image = parts[1]
            else:
                continue

            image = image.rstrip("&").strip()
            source_image = image  # 左边始终是原镜像

            # 生成右边的镜像
            if mode == "offline":
                name_part = image.split(":")[0]
                if "/" not in name_part:
                    target_image = f"dockerhub.kubekey.local/library/{image}"
                else:
                    target_image = f"dockerhub.kubekey.local/{image}"
            else:  # online
                if "/" in image:
                    name_mod = image.replace("/", ".", 1)  # 只替换第一个 /
                else:
                    name_mod = image
                target_image = f"registry.cn-shenzhen.aliyuncs.com/os_mirror/{name_mod}"

            # 分类
            if source_image.startswith("ccr.ccs.tencentyun.com"):
                tencent_images[source_image] = target_image
            else:
                other_images[source_image] = target_image

    # 写 YAML 文件
    with open(output_dir / "tencent.yaml", "w", encoding="utf-8") as f:
        yaml.dump(tencent_images, f, sort_keys=False)
    with open(output_dir / "basic.yaml", "w", encoding="utf-8") as f:
        yaml.dump(other_images, f, sort_keys=False)

    print(f"✅ {mode} 模式 YAML 文件已生成到 {output_dir}/")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"用法: python {sys.argv[0]} <offline|online>")
        sys.exit(1)

    mode = sys.argv[1]
    generate_yaml("pull_images.sh", mode)