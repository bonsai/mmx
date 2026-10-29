import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const host = document.querySelector("#viewer");
const status = document.querySelector("#status");
const modelStatus = document.querySelector("#model-status");
const exportStatus = document.querySelector("#export-status");
const scene = new THREE.Scene();
scene.background = new THREE.Color("#151e2a");

const camera = new THREE.PerspectiveCamera(45, 1, 0.01, 100000);
camera.position.set(3, 2, 4);

const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1;
host.appendChild(renderer.domElement);

scene.add(new THREE.HemisphereLight(0xdceaff, 0x303744, 2));
const keyLight = new THREE.DirectionalLight(0xffffff, 3);
keyLight.position.set(4, 6, 5);
scene.add(keyLight);
const fillLight = new THREE.DirectionalLight(0x9dbfff, 1.2);
fillLight.position.set(-4, 2, -3);
scene.add(fillLight);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.target.set(0, 0, 0);

const grid = new THREE.GridHelper(10, 20, 0x52657b, 0x293748);
scene.add(grid);

let model = null;
let initialCamera = camera.position.clone();
let initialTarget = controls.target.clone();

function resize() {
  const width = host.clientWidth;
  const height = host.clientHeight;
  if (!width || !height) return;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height, false);
}
new ResizeObserver(resize).observe(host);
resize();

document.querySelector("#reset-view").addEventListener("click", () => {
  camera.position.copy(initialCamera);
  controls.target.copy(initialTarget);
  controls.update();
});

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

document.querySelector("#export-png").addEventListener("click", () => {
  renderer.render(scene, camera);
  renderer.domElement.toBlob((blob) => {
    if (!blob) {
      exportStatus.textContent = "PNG export failed. Try again after the model has loaded.";
      return;
    }
    downloadBlob(blob, "mmx-preview.png");
    exportStatus.textContent = "PNG preview downloaded.";
  }, "image/png");
});

document.querySelector("#export-svg").addEventListener("click", () => {
  if (!model) {
    exportStatus.textContent = "Wait for the model to load before exporting SVG.";
    return;
  }
  const width = Math.max(host.clientWidth, 1);
  const height = Math.max(host.clientHeight, 1);
  camera.updateMatrixWorld(true);
  model.updateMatrixWorld(true);
  const paths = [];
  const vector = new THREE.Vector3();
  const maxTriangles = 60000;
  let triangleCount = 0;

  model.traverse((object) => {
    if (!object.isMesh || !object.geometry?.attributes?.position) return;
    const geometry = object.geometry;
    const positions = geometry.attributes.position;
    const index = geometry.index;
    const count = index ? index.count : positions.count;
    const materialColor = object.material?.color
      ? "#" + object.material.color.getHexString()
      : "#b7cbe3";
    for (let i = 0; i + 2 < count && triangleCount < maxTriangles; i += 3) {
      const ids = index ? [index.getX(i), index.getX(i + 1), index.getX(i + 2)] : [i, i + 1, i + 2];
      const points = ids.map((id) => {
        vector.fromBufferAttribute(positions, id).applyMatrix4(object.matrixWorld).project(camera);
        return { x: (vector.x * 0.5 + 0.5) * width, y: (-vector.y * 0.5 + 0.5) * height, z: vector.z };
      });
      if (points.some((p) => p.z < -1.2 || p.z > 1.2)) continue;
      const d = points.map((p, n) => `${n ? "L" : "M"}${p.x.toFixed(2)} ${p.y.toFixed(2)}`).join(" ") + " Z";
      paths.push(`<path d="${d}" fill="none" stroke="${materialColor}" stroke-opacity=".72" stroke-width=".65"/>`);
      triangleCount++;
    }
  });

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}"><rect width="100%" height="100%" fill="#151e2a"/>${paths.join("")}</svg>`;
  downloadBlob(new Blob([svg], { type: "image/svg+xml;charset=utf-8" }), "mmx-wireframe.svg");
  exportStatus.textContent = `SVG wireframe downloaded (${triangleCount.toLocaleString()} triangles projected). SVG is a 2D view, not an editable 3D model.`;
});

const loader = new GLTFLoader();
loader.load(
  "./models/mmx_lowpoly.glb",
  (gltf) => {
    model = gltf.scene;
    scene.add(model);

    const bounds = new THREE.Box3().setFromObject(model);
    const size = bounds.getSize(new THREE.Vector3());
    const center = bounds.getCenter(new THREE.Vector3());
    model.position.sub(center);

    const maxDimension = Math.max(size.x, size.y, size.z, 0.001);
    camera.near = maxDimension / 10000;
    camera.far = maxDimension * 100;
    camera.position.set(maxDimension * 1.7, maxDimension * 1.1, maxDimension * 1.7);
    camera.updateProjectionMatrix();
    controls.target.set(0, 0, 0);
    controls.minDistance = maxDimension * 0.05;
    controls.maxDistance = maxDimension * 20;
    controls.update();

    grid.scale.setScalar(Math.max(maxDimension / 10, 0.001));
    initialCamera = camera.position.clone();
    initialTarget = controls.target.clone();

    status.hidden = true;
    modelStatus.textContent =
      `Loaded · ${model.children.length || "model"} root child node(s) · bounds ${size.x.toFixed(2)} × ${size.y.toFixed(2)} × ${size.z.toFixed(2)} model units`;
  },
  undefined,
  (error) => {
    console.error("Could not load web/models/mmx_lowpoly.glb", error);
    status.classList.add("error");
    status.textContent = "Model not found. Check web/models/mmx_lowpoly.glb.";
    modelStatus.textContent = "Could not load web/models/mmx_lowpoly.glb.";
  }
);

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();
