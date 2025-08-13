import yaml
import sys
from pathlib import Path


online_registry = "registry.cn-shenzhen.aliyuncs.com/os_mirror"
# online_registry = "ccr.ccs.tencentyun.com/os_mirror"

offline_registry = "dockerhub.kubekey.local"


def convert_for_online(image: str) -> str:
    """将镜像转为 online 模式的 os_mirror 格式"""
    if image.startswith("ccr.ccs.tencentyun.com/"):
        image = image[len("ccr.ccs.tencentyun.com/"):]
        if "/" in image:
            image = image.split("/", 1)[1]

    if ":" in image:
        repo, tag = image.rsplit(":", 1)
        repo = repo.replace("/", ".")
        return f"{repo}:{tag}"
    else:
        return image.replace("/", ".")

def convert_for_offline(image: str) -> str:
    """将镜像转为 offline 模式的 dockerhub.kubekey.local 格式"""
    if image.startswith("ccr.ccs.tencentyun.com/"):
        image = image[len("ccr.ccs.tencentyun.com/"):]
        return f"{offline_registry}/{image}"
    else:
        name_part = image.split(":")[0]
        if "/" not in name_part:
            return f"{offline_registry}/library/{image}"
        else:
            return f"{offline_registry}/{image}"

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
            source_image = image

            if mode == "offline":
                target_image = convert_for_offline(image)
            else:
                target_image = f"{online_registry}/{convert_for_online(image)}"

            if source_image.startswith("ccr.ccs.tencentyun.com"):
                tencent_images[source_image] = target_image
            else:
                other_images[source_image] = target_image

    with open(output_dir / "tencent.yaml", "w", encoding="utf-8") as f:
        yaml.dump(tencent_images, f, sort_keys=False, allow_unicode=True)
    with open(output_dir / "basic.yaml", "w", encoding="utf-8") as f:
        yaml.dump(other_images, f, sort_keys=False, allow_unicode=True)

    print(f"✅ {mode} 模式 YAML 文件已生成到 {output_dir}/")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"用法: python {sys.argv[0]} <offline|online>")
        sys.exit(1)

    mode = sys.argv[1]
    generate_yaml("pull_images.sh", mode)