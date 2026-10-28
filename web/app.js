import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const host = document.querySelector("#viewer");
const status = document.querySelector("#status");
const modelStatus = document.querySelector("#model-status");
const scene = new THREE.Scene();
scene.background = new THREE.Color("#151e2a");

const camera = new THREE.PerspectiveCamera(45, 1, 0.01, 100000);
camera.position.set(3, 2, 4);

const renderer = new THREE.WebGLRenderer({ antialias: true });
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
    console.error("Could not load web/models/mmx.glb", error);
    status.classList.add("error");
    status.textContent = "Model not found. Export web/models/mmx.glb using blender/import_mmx.py.";
    modelStatus.textContent = "Could not load web/models/mmx_lowpoly.glb.";
  }
);

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();
