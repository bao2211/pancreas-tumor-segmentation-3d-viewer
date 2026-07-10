import 'package:flutter/material.dart';
import 'dart:html' as html;
import '../theme/app_theme.dart';

class Volume3DViewer extends StatefulWidget {
  final String gltfData;  // URL to GLB model
  final Map<String, dynamic>? volumeData;  // Optional: volume texture data
  final VoidCallback? onClose;
  
  const Volume3DViewer({
    super.key,
    required this.gltfData,
    this.volumeData,
    this.onClose,
  });
  
  @override
  State<Volume3DViewer> createState() => _Volume3DViewerState();
}

class _Volume3DViewerState extends State<Volume3DViewer> {
  html.WindowBase? _viewerWindow;
  
  @override
  void initState() {
    super.initState();
    print('Volume3DViewer initialized with gltfData: ${widget.gltfData.substring(0, 50)}...');
    _openViewer();
  }
  
  void _openViewer() {
    // Capture the gltfData for use in HTML
    final modelSrc = widget.gltfData;
    print('Opening viewer with modelSrc length: ${modelSrc.length}');
    print('ModelSrc starts with: ${modelSrc.substring(0, 100)}');
    
    // Create HTML content with Three.js
    const htmlContent = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>3D Pancreas & Tumor Visualization</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <style>
    * {
      box-sizing: border-box;
    }
    body {
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      background: #0F172A;
      color: #E2E8F0;
      overflow: hidden;
    }
    .container {
      display: flex;
      height: 100vh;
    }
    .viewer-container {
      flex: 1;
      position: relative;
    }
    #canvas3d {
      width: 100%;
      height: 100%;
      display: block;
    }
    .sidebar {
      width: 320px;
      background: rgba(30, 41, 59, 0.95);
      backdrop-filter: blur(10px);
      display: flex;
      flex-direction: column;
      box-shadow: -4px 0 20px rgba(0, 0, 0, 0.3);
      z-index: 10;
    }
    .sidebar-header {
      padding: 20px;
      border-bottom: 1px solid rgba(148, 163, 184, 0.2);
    }
    .title {
      font-size: 18px;
      font-weight: 700;
      margin: 0 0 8px 0;
      color: #06B6D4;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .subtitle {
      font-size: 13px;
      color: #94A3B8;
      margin: 0;
    }
    .sidebar-content {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
    }
    .section {
      margin-bottom: 24px;
    }
    .section-title {
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #64748B;
      margin: 0 0 12px 0;
    }
    .control-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
      padding: 8px 12px;
      background: rgba(15, 23, 42, 0.5);
      border-radius: 6px;
    }
    .control-label {
      font-size: 13px;
      color: #CBD5E1;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .switch {
      position: relative;
      display: inline-block;
      width: 42px;
      height: 24px;
    }
    .switch input {
      opacity: 0;
      width: 0;
      height: 0;
    }
    .slider {
      position: absolute;
      cursor: pointer;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: #475569;
      transition: .3s;
      border-radius: 24px;
    }
    .slider:before {
      position: absolute;
      content: "";
      height: 18px;
      width: 18px;
      left: 3px;
      bottom: 3px;
      background-color: white;
      transition: .3s;
      border-radius: 50%;
    }
    input:checked + .slider {
      background-color: #06B6D4;
    }
    input:checked + .slider:before {
      transform: translateX(18px);
    }
    .range-control {
      width: 100%;
      margin-bottom: 16px;
    }
    .range-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }
    .range-label {
      font-size: 13px;
      color: #CBD5E1;
    }
    .range-value {
      font-size: 13px;
      color: #06B6D4;
      font-weight: 600;
      font-family: 'Courier New', monospace;
    }
    input[type="range"] {
      width: 100%;
      height: 4px;
      border-radius: 2px;
      background: #334155;
      outline: none;
      -webkit-appearance: none;
    }
    input[type="range"]::-webkit-slider-thumb {
      -webkit-appearance: none;
      appearance: none;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: #06B6D4;
      cursor: pointer;
      border: 2px solid #0F172A;
    }
    input[type="range"]::-moz-range-thumb {
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: #06B6D4;
      cursor: pointer;
      border: 2px solid #0F172A;
    }
    .btn {
      width: 100%;
      padding: 12px;
      border: none;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      margin-bottom: 8px;
    }
    .btn-primary {
      background: #3B82F6;
      color: white;
    }
    .btn-primary:hover {
      background: #2563EB;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    .btn-secondary {
      background: rgba(100, 116, 139, 0.3);
      color: #CBD5E1;
      border: 1px solid rgba(148, 163, 184, 0.2);
    }
    .btn-secondary:hover {
      background: rgba(100, 116, 139, 0.5);
      border-color: rgba(148, 163, 184, 0.4);
    }
    .btn-danger {
      background: rgba(239, 68, 68, 0.2);
      color: #FCA5A5;
      border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .btn-danger:hover {
      background: rgba(239, 68, 68, 0.3);
      border-color: rgba(239, 68, 68, 0.5);
    }
    .legend {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .legend-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 12px;
      background: rgba(15, 23, 42, 0.5);
      border-radius: 6px;
    }
    .legend-color {
      width: 24px;
      height: 24px;
      border-radius: 4px;
      flex-shrink: 0;
    }
    .legend-label {
      font-size: 13px;
      color: #CBD5E1;
      flex: 1;
    }
    .legend-cyan {
      background: linear-gradient(135deg, rgba(6, 182, 212, 0.4), rgba(6, 182, 212, 0.8));
      border: 2px solid #06B6D4;
    }
    .legend-red {
      background: linear-gradient(135deg, rgba(239, 68, 68, 0.4), rgba(239, 68, 68, 0.8));
      border: 2px solid #EF4444;
    }
    .legend-gray {
      background: linear-gradient(135deg, rgba(148, 163, 184, 0.2), rgba(148, 163, 184, 0.4));
      border: 2px solid #64748B;
    }
    .loading {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      text-align: center;
      z-index: 100;
      background: rgba(30, 41, 59, 0.95);
      padding: 40px;
      border-radius: 12px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    }
    .spinner {
      border: 3px solid rgba(6, 182, 212, 0.2);
      border-top: 3px solid #06B6D4;
      border-radius: 50%;
      width: 48px;
      height: 48px;
      animation: spin 0.8s linear infinite;
      margin: 0 auto 20px;
    }
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    .loading-text {
      font-size: 14px;
      color: #94A3B8;
    }
    .info-panel {
      position: absolute;
      top: 16px;
      left: 16px;
      background: rgba(30, 41, 59, 0.95);
      backdrop-filter: blur(10px);
      padding: 16px;
      border-radius: 8px;
      max-width: 300px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .info-item {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
      font-size: 13px;
    }
    .info-label {
      color: #94A3B8;
    }
    .info-value {
      color: #06B6D4;
      font-weight: 600;
      font-family: 'Courier New', monospace;
    }
    .shortcuts {
      background: rgba(15, 23, 42, 0.5);
      padding: 12px;
      border-radius: 6px;
      font-size: 12px;
      line-height: 1.6;
      color: #94A3B8;
    }
    .shortcuts strong {
      color: #CBD5E1;
    }
    ::-webkit-scrollbar {
      width: 6px;
    }
    ::-webkit-scrollbar-track {
      background: rgba(15, 23, 42, 0.5);
    }
    ::-webkit-scrollbar-thumb {
      background: #475569;
      border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #64748B;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="viewer-container">
      <div class="loading" id="loading">
        <div class="spinner"></div>
        <div class="loading-text">Loading 3D visualization...</div>
      </div>
      
      <div class="info-panel" id="infoPanel" style="display: none;">
        <div class="info-item">
          <span class="info-label">Vertices:</span>
          <span class="info-value" id="vertexCount">-</span>
        </div>
        <div class="info-item">
          <span class="info-label">Faces:</span>
          <span class="info-value" id="faceCount">-</span>
        </div>
        <div class="info-item">
          <span class="info-label">FPS:</span>
          <span class="info-value" id="fpsCount">60</span>
        </div>
      </div>
      
      <canvas id="canvas3d"></canvas>
    </div>
    
    <div class="sidebar">
      <div class="sidebar-header">
        <h1 class="title">
          <span>🔬</span>
          <span>3D Viewer</span>
        </h1>
        <p class="subtitle">Pancreas & Tumor Visualization</p>
      </div>
      
      <div class="sidebar-content">
        <!-- Legend Section -->
        <div class="section">
          <div class="section-title">🎨 ANATOMY LEGEND</div>
          <div class="legend">
            <div class="legend-item">
              <div class="legend-color legend-cyan"></div>
              <span class="legend-label">Pancreas Tissue (Cyan)</span>
            </div>
            <div class="legend-item">
              <div class="legend-color legend-red"></div>
              <span class="legend-label">Tumor Region</span>
            </div>
            <div class="legend-item" id="volumeLegend" style="display: none;">
              <div class="legend-color legend-gray"></div>
              <span class="legend-label">CT Volume</span>
            </div>
          </div>
        </div>
        
        <!-- Visibility Section -->
        <div class="section">
          <div class="section-title">👁️ VISIBILITY</div>
          <div class="control-row">
            <span class="control-label">
              <span>🫁</span>
              <span>Pancreas</span>
            </span>
            <label class="switch">
              <input type="checkbox" id="showPancreas" checked>
              <span class="slider"></span>
            </label>
          </div>
          <div class="control-row">
            <span class="control-label">
              <span>🔴</span>
              <span>Tumor</span>
            </span>
            <label class="switch">
              <input type="checkbox" id="showTumor" checked>
              <span class="slider"></span>
            </label>
          </div>
          <div class="control-row" id="volumeToggle" style="display: none;">
            <span class="control-label">
              <span>🔲</span>
              <span>CT Volume</span>
            </span>
            <label class="switch">
              <input type="checkbox" id="showVolume" checked>
              <span class="slider"></span>
            </label>
          </div>
          <div class="control-row" id="markersToggle" style="display: none;">
            <span class="control-label">
              <span>📍</span>
              <span>Debug Markers</span>
            </span>
            <label class="switch">
              <input type="checkbox" id="showMarkers" checked>
              <span class="slider"></span>
            </label>
          </div>
        </div>
        
        <!-- Opacity Section -->
        <div class="section" id="opacitySection" style="display: none;">
          <div class="section-title">🌫️ OPACITY</div>
          <div class="range-control">
            <div class="range-header">
              <span class="range-label">CT Volume</span>
              <span class="range-value" id="volumeOpacityValue">0.15</span>
            </div>
            <input type="range" id="volumeOpacity" min="0" max="1" step="0.01" value="0.15">
          </div>
        </div>
        
        <!-- Camera Section -->
        <div class="section">
          <div class="section-title">📷 CAMERA</div>
          <button class="btn btn-primary" onclick="focusOnSegmentation()">
            <span>🔍</span>
            <span>Focus on Detection</span>
          </button>
          <button class="btn btn-secondary" onclick="resetCamera()">
            <span>🔄</span>
            <span>Reset View</span>
          </button>
          <button class="btn btn-secondary" onclick="toggleStats()">
            <span>📊</span>
            <span id="statsButtonText">Show Stats</span>
          </button>
        </div>
        
        <!-- Controls Guide -->
        <div class="section">
          <div class="section-title">⌨️ CONTROLS</div>
          <div class="shortcuts">
            <strong>🖱️ Mouse:</strong><br>
            • Left-click + drag → Rotate<br>
            • Scroll wheel → Zoom<br>
            • Right-click + drag → Pan<br>
            <br>
            <strong>⌨️ Keyboard:</strong><br>
            • R → Reset camera<br>
            • F → Focus on detection<br>
            • S → Toggle stats<br>
          </div>
        </div>
        
        <!-- Exit Button -->
        <div class="section">
          <button class="btn btn-danger" onclick="window.close()">
            <span>✖️</span>
            <span>Close Viewer</span>
          </button>
        </div>
      </div>
    </div>
  </div>
  
  <script>
    const canvas = document.getElementById('canvas3d');
    const loading = document.querySelector('#loading');
    
    let scene, camera, renderer, controls, model, modelGroup;
    let directionalLight, ambientLight;
    let volumeMesh = null;
    let volumeData = null;
    let pancreasVolumeMesh = null;
    let tumorVolumeMesh = null;
    
    // Volume rendering shaders (GLSL ES 3.00 for WebGL 2.0)
    // Note: Do NOT add #version directive - Three.js handles it via glslVersion parameter
    const volumeVertexShader = `
      out vec3 vWorldPosition;
      out vec3 vLocalPosition;
      
      void main() {
        vLocalPosition = position;
        vec4 worldPos = modelMatrix * vec4(position, 1.0);
        vWorldPosition = worldPos.xyz;
        gl_Position = projectionMatrix * viewMatrix * worldPos;
      }
    `;
    
    const volumeFragmentShader = `
      precision highp float;
      precision highp sampler3D;
      
      uniform sampler3D volumeTexture;
      uniform vec3 cameraPos;
      uniform float opacity;
      uniform float windowMin;
      uniform float windowMax;
      
      in vec3 vWorldPosition;
      in vec3 vLocalPosition;
      
      out vec4 fragColor;
      
      // Transfer function: value to RGBA
      vec4 transferFunction(float value) {
        // Value is already normalized to 0-255 from the texture
        // Server already applied windowing, so normalize to 0-1
        float normalized = value / 255.0;
        
        vec4 color;
        
        // Apply color mapping based on normalized value
        // More aggressive transparency for low values
        if (normalized < 0.05) {
          // Air/background - fully transparent
          color = vec4(0.0, 0.0, 0.0, 0.0);
        } else if (normalized < 0.3) {
          // Low density soft tissue - very transparent
          float t = (normalized - 0.05) / 0.25;
          color = vec4(0.2, 0.15, 0.15, 0.02 * t * opacity);
        } else if (normalized < 0.5) {
          // Medium density soft tissue - slightly transparent
          float t = (normalized - 0.3) / 0.2;
          color = vec4(0.6 + t * 0.2, 0.4 + t * 0.2, 0.3 + t * 0.2, 0.05 * (1.0 + t) * opacity);
        } else if (normalized < 0.7) {
          // Dense tissue - more visible
          float t = (normalized - 0.5) / 0.2;
          color = vec4(0.8 + t * 0.1, 0.7 + t * 0.2, 0.6, 0.1 * (1.0 + t * 2.0) * opacity);
        } else {
          // Bone - most visible
          float t = (normalized - 0.7) / 0.3;
          color = vec4(0.95, 0.95, 0.95, (0.2 + 0.5 * t) * opacity);
        }
        
        return color;
      }
      
      void main() {
        // Ray direction from camera through this fragment
        vec3 rayDir = normalize(vWorldPosition - cameraPos);
        
        // Box bounds in local space
        vec3 boxMin = vec3(-0.5);
        vec3 boxMax = vec3(0.5);
        
        // Ray-box intersection
        vec3 invRayDir = 1.0 / (rayDir + 0.00001); // Avoid division by zero
        vec3 t0 = (boxMin - vLocalPosition) * invRayDir;
        vec3 t1 = (boxMax - vLocalPosition) * invRayDir;
        
        vec3 tNear3 = min(t0, t1);
        vec3 tFar3 = max(t0, t1);
        
        float tNear = max(max(tNear3.x, tNear3.y), tNear3.z);
        float tFar = min(min(tFar3.x, tFar3.y), tFar3.z);
        
        // No intersection with box
        if (tNear > tFar || tFar < 0.0) {
          discard;
        }
        
        // Start point: either entry to box or current position if inside
        float rayStart = max(0.0, tNear);
        float rayEnd = tFar;
        
        // Ray marching through volume
        const int numSteps = 96;
        float stepSize = (rayEnd - rayStart) / float(numSteps);
        
        vec4 color = vec4(0.0);
        
        for (int i = 0; i < numSteps; i++) {
          // Current position along ray
          float t = rayStart + stepSize * (float(i) + 0.5);
          vec3 pos = vLocalPosition + t * rayDir;
          
          // Convert to texture coordinates [0, 1]
          vec3 texCoord = pos + 0.5;
          
          // Clamp to valid range (should always be valid but just in case)
          texCoord = clamp(texCoord, 0.0, 1.0);
          
          // Sample volume texture
          float intensity = texture(volumeTexture, texCoord).r * 255.0;
          
          // Get color and opacity from transfer function
          vec4 src = transferFunction(intensity);
          
          // Front-to-back compositing
          src.rgb *= src.a;
          color = color + (1.0 - color.a) * src;
          
          // Early ray termination
          if (color.a > 0.95) {
            break;
          }
        }
        
        // Output final color
        fragColor = color;
      }
    `;
    
    // Segmentation volume shaders (for pancreas and tumor)
    const segmentationVertexShader = `
      out vec3 vWorldPosition;
      out vec3 vLocalPosition;
      
      void main() {
        vLocalPosition = position;
        vec4 worldPosition = modelMatrix * vec4(position, 1.0);
        vWorldPosition = worldPosition.xyz;
        gl_Position = projectionMatrix * viewMatrix * worldPosition;
      }
    `;
    
    const segmentationFragmentShader = `
      precision highp float;
      precision highp sampler3D;
      
      uniform sampler3D segmentationTexture;
      uniform vec3 cameraPos;
      uniform float opacity;
      uniform vec3 segmentColor;
      
      in vec3 vWorldPosition;
      in vec3 vLocalPosition;
      
      out vec4 fragColor;
      
      // Ray-box intersection
      vec2 rayBoxIntersection(vec3 rayOrigin, vec3 rayDir, vec3 boxMin, vec3 boxMax) {
        vec3 invDir = 1.0 / rayDir;
        vec3 tMin = (boxMin - rayOrigin) * invDir;
        vec3 tMax = (boxMax - rayOrigin) * invDir;
        vec3 t1 = min(tMin, tMax);
        vec3 t2 = max(tMin, tMax);
        float tNear = max(max(t1.x, t1.y), t1.z);
        float tFar = min(min(t2.x, t2.y), t2.z);
        return vec2(tNear, tFar);
      }
      
      void main() {
        // Ray from camera through fragment
        vec3 rayDir = normalize(vWorldPosition - cameraPos);
        vec3 rayOrigin = vLocalPosition;
        
        // Intersect with volume box
        vec3 boxMin = vec3(-0.5);
        vec3 boxMax = vec3(0.5);
        vec2 tHit = rayBoxIntersection(rayOrigin, rayDir, boxMin, boxMax);
        
        if (tHit.x > tHit.y || tHit.y < 0.0) {
          discard;
        }
        
        tHit.x = max(tHit.x, 0.0);
        
        // Ray marching with more steps for sparse segmentation data
        vec3 rayStart = rayOrigin + rayDir * tHit.x;
        vec3 rayEnd = rayOrigin + rayDir * tHit.y;
        float rayLength = distance(rayStart, rayEnd);
        
        int numSteps = 256;  // Increased from 128 to 256 for better sampling
        float stepSize = rayLength / float(numSteps);
        
        vec4 color = vec4(0.0);
        
        for (int i = 0; i < numSteps; i++) {
          vec3 samplePos = rayStart + rayDir * (float(i) * stepSize);
          vec3 texCoord = samplePos + 0.5;
          
          // Sample segmentation mask (binary: 0 or 1)
          float mask = texture(segmentationTexture, texCoord).r;
          
          if (mask > 0.001) {  // Very low threshold to catch any non-zero voxels
            // Hit the segmentation - use solid color with brightness based on mask value
            float alpha = opacity * mask * 255.0;  // Scale up if mask values are 0-1 range
            alpha = min(alpha, 1.0);  // Clamp to max 1.0
            vec3 rgb = segmentColor;
            
            // Front-to-back compositing
            color.rgb += (1.0 - color.a) * alpha * rgb;
            color.a += (1.0 - color.a) * alpha;
            
            if (color.a > 0.95) break;
          }
        }
        
        fragColor = color;
      }
    `;
    
    // Initialize Three.js
    function initThreeJS() {
      console.log('Initializing Three.js...');
      console.log('Canvas dimensions:', canvas.clientWidth, 'x', canvas.clientHeight);
      
      // Scene
      scene = new THREE.Scene();
      scene.background = new THREE.Color(0x1E293B);
      
      // Camera
      const aspect = canvas.clientWidth / canvas.clientHeight;
      console.log('Camera aspect ratio:', aspect);
      camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 1000);
      camera.position.set(3, 2, 5);
      camera.lookAt(0, 0, 0);
      
      // Renderer with WebGL 2.0 (required for 3D textures)
      const gl = canvas.getContext('webgl2', { alpha: false });
      if (!gl) {
        console.error('WebGL 2.0 not supported!');
        alert('Your browser does not support WebGL 2.0, which is required for volume rendering.');
        return;
      }
      renderer = new THREE.WebGLRenderer({ canvas: canvas, context: gl, antialias: true });
      renderer.setSize(canvas.clientWidth, canvas.clientHeight);
      renderer.setPixelRatio(window.devicePixelRatio);
      console.log('✅ WebGL 2.0 renderer initialized');
      console.log('Renderer size:', renderer.domElement.width, 'x', renderer.domElement.height);
      
      // Lights
      ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
      scene.add(ambientLight);
      
      directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
      directionalLight.position.set(5, 10, 7.5);
      scene.add(directionalLight);
      
      console.log('Initial light intensity:', directionalLight.intensity);
      
      // Add small axes helper at origin
      const axesHelper = new THREE.AxesHelper(1);
      scene.add(axesHelper);
      
      console.log('Added axes helper');
      
      // Controls
      controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.minDistance = 0.5;
      controls.maxDistance = 10;
      
      // Handle resize
      window.addEventListener('resize', onWindowResize);
      
      console.log('✅ Three.js initialized');
      
      // Setup UI controls
      setupControls();
      
      // Start animation loop
      animate();
    }
    
    function onWindowResize() {
      camera.aspect = canvas.clientWidth / canvas.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    }
    
    function animate() {
      requestAnimationFrame(animate);
      
      // Update camera position in volume shaders
      if (volumeMesh && volumeMesh.material.uniforms) {
        volumeMesh.material.uniforms.cameraPos.value.copy(camera.position);
      }
      
      if (pancreasVolumeMesh && pancreasVolumeMesh.material.uniforms) {
        pancreasVolumeMesh.material.uniforms.cameraPos.value.copy(camera.position);
      }
      
      if (tumorVolumeMesh && tumorVolumeMesh.material.uniforms) {
        tumorVolumeMesh.material.uniforms.cameraPos.value.copy(camera.position);
      }
      
      controls.update();
      
      // Update stats
      updateStats();
      
      renderer.render(scene, camera);
    }
    
    // Function to create segmentation volume texture
    function createSegmentationTexture(base64Data, dimensions) {
      console.log('Creating segmentation texture...');
      console.log('Dimensions:', dimensions);
      
      const binaryString = atob(base64Data);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      let nonZero = 0;
      let maxVal = 0;
      let minNonZero = 255;
      for (let i = 0; i < bytes.length; i++) {
        if (bytes[i] > 0) {
          nonZero++;
          maxVal = Math.max(maxVal, bytes[i]);
          minNonZero = Math.min(minNonZero, bytes[i]);
        }
      }
      console.log(`Non-zero voxels: \${nonZero} / \${bytes.length} (\${(nonZero/bytes.length*100).toFixed(2)}%)`);
      console.log(`Value range: 0 to \${maxVal}, min non-zero: \${minNonZero}`);
      
      const texture = new THREE.DataTexture3D(
        bytes,
        dimensions[0],
        dimensions[1],
        dimensions[2]
      );
      
      texture.format = THREE.RedFormat;
      texture.type = THREE.UnsignedByteType;
      texture.minFilter = THREE.LinearFilter;
      texture.magFilter = THREE.LinearFilter;
      texture.wrapS = THREE.ClampToEdgeWrapping;
      texture.wrapT = THREE.ClampToEdgeWrapping;
      texture.wrapR = THREE.ClampToEdgeWrapping;
      texture.unpackAlignment = 1;
      texture.needsUpdate = true;
      
      return texture;
    }
    
    function loadGLBModel(url) {
      console.log('Loading GLB from:', url);
      console.log('URL type:', typeof url);
      console.log('URL length:', url.length);
      console.log('URL prefix:', url.substring(0, 50));
      loading.innerHTML = '<div class="spinner"></div><div>Loading 3D model...</div>';
      
      const loader = new THREE.GLTFLoader();
      
      loader.load(
        url,
        function(gltf) {
          console.log('✅ GLB loaded successfully!');
          console.log('GLTF scene:', gltf.scene);
          console.log('Scene children count:', gltf.scene.children.length);
          
          model = gltf.scene;
          
          // Traverse and log all meshes
          let meshCount = 0;
          let pancreasFound = false;
          let tumorFound = false;
          
          model.traverse((child) => {
            console.log('Child:', child.type, child.name || 'unnamed');
            
            if (child.isMesh) {
              meshCount++;
              const meshName = child.name || 'unnamed';
              console.log('Found mesh:', meshName);
              console.log('  Geometry:', child.geometry);
              console.log('  Vertices:', child.geometry.attributes.position ? child.geometry.attributes.position.count : 0);
              console.log('  Material:', child.material);
              console.log('  Material type:', child.material ? child.material.type : 'none');
              
              // Detect which mesh this is
              const isPancreas = meshName.toLowerCase().includes('pancreas');
              const isTumor = meshName.toLowerCase().includes('tumor');
              
              if (isPancreas) pancreasFound = true;
              if (isTumor) tumorFound = true;
              
              // Apply proper materials based on mesh type
              if (isTumor) {
                console.log('  Applying TUMOR material (red)');
                child.material = new THREE.MeshStandardMaterial({
                  color: 0xff0000,  // Red
                  side: THREE.DoubleSide,
                  metalness: 0.2,
                  roughness: 0.6,
                  opacity: 1.0,
                  transparent: false
                });
              } else if (isPancreas) {
                console.log('  Applying PANCREAS material (bright cyan)');
                child.material = new THREE.MeshStandardMaterial({
                  color: 0x00ffff,  // Cyan
                  side: THREE.DoubleSide,
                  metalness: 0.1,
                  roughness: 0.4,
                  opacity: 1.0,
                  transparent: false
                });
              } else {
                // Default: assume pancreas if not tumor
                console.log('  Applying DEFAULT material (cyan - assuming pancreas)');
                child.material = new THREE.MeshStandardMaterial({
                  color: 0x00ffff,
                  side: THREE.DoubleSide,
                  metalness: 0.1,
                  roughness: 0.4,
                  opacity: 1.0,
                  transparent: false
                });
              }
              
              // Make sure it's visible
              child.visible = true;
              child.frustumCulled = false;
              child.castShadow = true;
              child.receiveShadow = true;
            }
          });
          
          console.log('Total meshes found:', meshCount);
          console.log('Pancreas mesh found:', pancreasFound);
          console.log('Tumor mesh found:', tumorFound);
          
          if (meshCount === 0) {
            loading.innerHTML = '<div style="color: #EF4444;">❌ No meshes found in GLB file</div>';
            return;
          }
          
          // Get bounding box before adding to scene
          const box = new THREE.Box3().setFromObject(model);
          const size = box.getSize(new THREE.Vector3());
          const center = box.getCenter(new THREE.Vector3());
          
          console.log('Original model bounds:');
          console.log('  Size:', size);
          console.log('  Center:', center);
          
          // Check if bounding box is valid
          if (size.x === 0 || size.y === 0 || size.z === 0) {
            console.error('❌ Invalid bounding box - model has zero size!');
            loading.innerHTML = '<div style="color: #EF4444;">❌ Model has invalid geometry</div>';
            return;
          }
          
          // Create a group to hold the model
          modelGroup = new THREE.Group();
          modelGroup.add(model);
          scene.add(modelGroup);
          
          // Store model and bounds for later scaling when volume loads
          window.loadedModel = model;
          window.modelOriginalBounds = { size, center };
          
          console.log('✅ Model added to scene (will be scaled to match volume when volume loads)');
          console.log('Model bounds before scaling:', size);
          console.log('Model center before scaling:', center);
          
          // If volume already loaded, scale now
          if (volumeMesh) {
            console.log('Volume already exists, scaling model now...');
            scaleModelToMatchVolume();
          }
          
          // Position camera closer and looking at origin
          camera.position.set(4, 3, 4);
          camera.lookAt(0, 0, 0);
          controls.target.set(0, 0, 0);
          controls.minDistance = 2;
          controls.maxDistance = 20;
          controls.update();
          
          console.log('✅ Model centered at origin with scale:', modelGroup.scale);
          console.log('Camera at:', camera.position);
          
          // Hide loading
          loading.style.display = 'none';
          
          console.log('✅ Model configured and added to scene');
        },
        function(xhr) {
          if (xhr.total > 0) {
            const progress = (xhr.loaded / xhr.total) * 100;
            loading.innerHTML = '<div class="spinner"></div><div>Loading: ' + Math.round(progress) + '%</div>';
            console.log('Loading progress:', Math.round(progress) + '%');
          } else {
            console.log('Loading...', xhr.loaded, 'bytes');
          }
        },
        function(error) {
          console.error('❌ Error loading GLB:', error);
          console.error('Error details:', JSON.stringify(error, null, 2));
          loading.innerHTML = '<div style="color: #EF4444;">❌ Failed to load model<br/><small>' + (error.message || 'Unknown error') + '</small></div>';
        }
      );
    }
    
    // Scale model to match volume dimensions
    function scaleModelToMatchVolume() {
      if (!modelGroup || !window.modelOriginalBounds || !window.loadedModel || !window.volumeUniformScale) {
        console.log('Cannot scale model - missing required data');
        return;
      }
      
      console.log('🔧 Scaling segmentation models to match volume...');
      
      const { size: modelSize, center: modelCenter } = window.modelOriginalBounds;
      const model = window.loadedModel;
      const uniformScale = window.volumeUniformScale;
      
      console.log('Model original bounds:');
      console.log('  Size:', modelSize);
      console.log('  Center:', modelCenter);
      
      // The meshes are generated with voxel spacing in mm
      // The volume cube is uniformScale units (6 units)
      // Scale factor = volume size / mesh size in mm
      const volumeScale = uniformScale;
      const meshMaxDim = Math.max(modelSize.x, modelSize.y, modelSize.z);
      const scaleToVolume = volumeScale / meshMaxDim;
      
      console.log('Mesh max dimension (mm):', meshMaxDim);
      console.log('Volume cube size (units):', volumeScale);
      console.log('Scale factor:', scaleToVolume);
      
      // Center the model at origin first
      model.position.set(-modelCenter.x, -modelCenter.y, -modelCenter.z);
      
      // Scale model group to match volume
      modelGroup.scale.setScalar(scaleToVolume);
      
      console.log('✅ Segmentation models scaled');
      console.log('Model position offset:', model.position);
      console.log('Model group scale:', modelGroup.scale);
    }
    
    // Visualize detected regions with debug markers
    function visualizeDetectedRegions(regions, volumeScale, dimensions) {
      if (!regions || regions.length === 0) {
        console.log('No detected regions to visualize');
        return;
      }
      
      console.log(`🎯 Visualizing \${regions.length} detected regions`);
      
      // Remove previous markers if any
      const previousMarkers = scene.children.filter(obj => obj.name && obj.name.startsWith('region_marker_'));
      previousMarkers.forEach(marker => scene.remove(marker));
      
      regions.forEach((region, idx) => {
        // Convert voxel coordinates to normalized coordinates [-0.5, 0.5]
        const normalizedX = (region.centroid_voxel[0] / dimensions[0]) - 0.5;
        const normalizedY = (region.centroid_voxel[1] / dimensions[1]) - 0.5;
        const normalizedZ = (region.centroid_voxel[2] / dimensions[2]) - 0.5;
        
        // Apply volume scale to get scene coordinates
        const sceneX = normalizedX * volumeScale.x;
        const sceneY = normalizedY * volumeScale.y;
        const sceneZ = normalizedZ * volumeScale.z;
        
        // Create sphere marker
        const markerGeometry = new THREE.SphereGeometry(0.1, 16, 16);
        const markerColor = region.type === 'pancreas' ? 0x00FFFF : 0xFF0000; // Cyan for pancreas, red for tumor
        const markerMaterial = new THREE.MeshBasicMaterial({
          color: markerColor,
          transparent: true,
          opacity: 0.8
        });
        
        const marker = new THREE.Mesh(markerGeometry, markerMaterial);
        marker.position.set(sceneX, sceneY, sceneZ);
        marker.name = `region_marker_\${idx}_\${region.type}`;
        scene.add(marker);
        
        console.log(`  Marker \${idx} (\${region.type}):`, {
          voxel: region.centroid_voxel,
          normalized: [normalizedX, normalizedY, normalizedZ],
          scene: [sceneX, sceneY, sceneZ],
          physical_mm: region.centroid_physical
        });
        
        // Create bounding box wireframe if bbox available
        if (region.bbox_voxel) {
          const bbox = region.bbox_voxel;
          
          // Calculate bbox dimensions in normalized coordinates
          const bboxMinX = (bbox.min[0] / dimensions[0]) - 0.5;
          const bboxMinY = (bbox.min[1] / dimensions[1]) - 0.5;
          const bboxMinZ = (bbox.min[2] / dimensions[2]) - 0.5;
          const bboxMaxX = (bbox.max[0] / dimensions[0]) - 0.5;
          const bboxMaxY = (bbox.max[1] / dimensions[1]) - 0.5;
          const bboxMaxZ = (bbox.max[2] / dimensions[2]) - 0.5;
          
          const bboxWidth = (bboxMaxX - bboxMinX) * volumeScale.x;
          const bboxHeight = (bboxMaxY - bboxMinY) * volumeScale.y;
          const bboxDepth = (bboxMaxZ - bboxMinZ) * volumeScale.z;
          
          const bboxCenterX = ((bboxMinX + bboxMaxX) / 2) * volumeScale.x;
          const bboxCenterY = ((bboxMinY + bboxMaxY) / 2) * volumeScale.y;
          const bboxCenterZ = ((bboxMinZ + bboxMaxZ) / 2) * volumeScale.z;
          
          const bboxGeometry = new THREE.BoxGeometry(bboxWidth, bboxHeight, bboxDepth);
          const bboxMaterial = new THREE.MeshBasicMaterial({
            color: markerColor,
            wireframe: true,
            transparent: true,
            opacity: 0.5
          });
          
          const bboxMesh = new THREE.Mesh(bboxGeometry, bboxMaterial);
          bboxMesh.position.set(bboxCenterX, bboxCenterY, bboxCenterZ);
          bboxMesh.name = `region_bbox_\${idx}_\${region.type}`;
          scene.add(bboxMesh);
        }
      });
      
      console.log('✅ Region markers added to scene');
    }
    
    // Load volume data as 3D texture
    function loadVolumeData(volumeInfo) {
      console.log('Loading volume data...', volumeInfo);
      
      const { volume_data, dimensions, spacing, window_min, window_max, spatial_metadata } = volumeInfo;
      
      // Log spatial metadata if available
      if (spatial_metadata) {
        console.log('📍 Spatial Metadata Available:');
        console.log('  Original affine matrix:', spatial_metadata.original_affine);
        console.log('  Original spacing (mm):', spatial_metadata.original_spacing);
        console.log('  Original shape:', spatial_metadata.original_shape);
        console.log('  Original origin:', spatial_metadata.original_origin);
        console.log('  Resampling transform:', spatial_metadata.resampling_transform);
        console.log('  Detected regions:', spatial_metadata.detected_regions ? spatial_metadata.detected_regions.length : 0);
        
        if (spatial_metadata.detected_regions) {
          spatial_metadata.detected_regions.forEach((region, idx) => {
            console.log(`  Region \${idx}: \${region.type} at slice \${region.slice_idx}`);
            console.log(`    Centroid (physical mm):`, region.centroid_physical);
            console.log(`    Voxel count:`, region.voxel_count);
          });
        }
      }
      
      if (!volume_data || !dimensions) {
        console.error('Invalid volume data');
        return;
      }
      
      console.log('Volume dimensions:', dimensions);
      console.log('Window:', window_min, 'to', window_max);
      
      try {
        // Decode base64 to Uint8Array
        const binaryString = atob(volume_data);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        
        console.log('Decoded volume data:', bytes.length, 'bytes');
        console.log('Expected size:', dimensions[0] * dimensions[1] * dimensions[2]);
        console.log('Size match:', bytes.length === dimensions[0] * dimensions[1] * dimensions[2]);
        console.log('First 20 values:', Array.from(bytes.slice(0, 20)));
        console.log('Middle 20 values:', Array.from(bytes.slice(bytes.length/2, bytes.length/2 + 20)));
        console.log('Last 20 values:', Array.from(bytes.slice(-20)));
        
        // Verify data is not all zeros or random
        const nonZero = Array.from(bytes).filter(v => v > 0).length;
        console.log('Non-zero values:', nonZero, '/', bytes.length, '(', (nonZero/bytes.length*100).toFixed(1), '%)');
        
        // Create 3D texture (THREE.DataTexture3D for r128)
        const texture = new THREE.DataTexture3D(
          bytes,
          dimensions[0],
          dimensions[1],
          dimensions[2]
        );
        texture.format = THREE.RedFormat;
        texture.type = THREE.UnsignedByteType;
        texture.minFilter = THREE.LinearFilter;
        texture.magFilter = THREE.LinearFilter;
        texture.wrapS = THREE.ClampToEdgeWrapping;
        texture.wrapT = THREE.ClampToEdgeWrapping;
        texture.wrapR = THREE.ClampToEdgeWrapping;
        texture.unpackAlignment = 1;
        texture.needsUpdate = true;
        
        console.log('✅ 3D texture created');
        console.log('Texture format:', texture.format);
        console.log('Texture type:', texture.type);
        console.log('Texture dimensions:', dimensions);
        
        // Create volume material with shader
        const volumeMaterial = new THREE.ShaderMaterial({
          vertexShader: volumeVertexShader,
          fragmentShader: volumeFragmentShader,
          uniforms: {
            volumeTexture: { value: texture },
            cameraPos: { value: camera.position },
            opacity: { value: 0.15 },
            windowMin: { value: window_min },
            windowMax: { value: window_max }
          },
          transparent: true,
          side: THREE.DoubleSide,  // Render both sides
          depthWrite: false,
          depthTest: false,  // Disable depth test for proper blending
          blending: THREE.NormalBlending,
          glslVersion: THREE.GLSL3 // Use GLSL ES 3.00 for WebGL 2.0
        });
        
        console.log('✅ Volume material created');
        
        // Create volume geometry - use unit cube, then scale to match scene
        const volumeGeometry = new THREE.BoxGeometry(1, 1, 1);
        
        // Remove old volume mesh if exists
        if (volumeMesh) {
          scene.remove(volumeMesh);
          volumeMesh.geometry.dispose();
          volumeMesh.material.dispose();
        }
        
        // Create volume mesh
        volumeMesh = new THREE.Mesh(volumeGeometry, volumeMaterial);
        volumeMesh.name = 'volumeMesh';
        
        // Calculate scale based on physical spacing if spatial_metadata available
        let scaleX, scaleY, scaleZ;
        let baseScale = 6; // Base scale for visualization
        
        if (spatial_metadata && spatial_metadata.resampling_transform) {
          // Use physical spacing after resampling to maintain correct proportions
          const physicalSpacing = spatial_metadata.resampling_transform.new_spacing;
          console.log('🎯 Using physical spacing for anatomically correct scale:', physicalSpacing);
          
          // Calculate physical dimensions in mm
          const physicalDimX = dimensions[0] * physicalSpacing[0];
          const physicalDimY = dimensions[1] * physicalSpacing[1];
          const physicalDimZ = dimensions[2] * physicalSpacing[2];
          
          console.log('Physical dimensions (mm):', [physicalDimX, physicalDimY, physicalDimZ]);
          
          // Normalize to largest dimension and scale
          const maxDim = Math.max(physicalDimX, physicalDimY, physicalDimZ);
          scaleX = (physicalDimX / maxDim) * baseScale;
          scaleY = (physicalDimY / maxDim) * baseScale;
          scaleZ = (physicalDimZ / maxDim) * baseScale;
          
          console.log('Anatomically correct scale factors:', [scaleX, scaleY, scaleZ]);
        } else {
          // Fallback to uniform scale if no spatial metadata
          console.log('⚠️ No spatial metadata, using uniform scale');
          scaleX = scaleY = scaleZ = baseScale;
        }
        
        volumeMesh.scale.set(scaleX, scaleY, scaleZ);
        volumeMesh.position.set(0, 0, 0);
        
        scene.add(volumeMesh);
        
        // Add a wireframe helper to visualize the volume bounds
        const wireframeGeo = new THREE.BoxGeometry(1, 1, 1);
        const wireframeMat = new THREE.MeshBasicMaterial({
          color: 0x00ff00,
          wireframe: true,
          transparent: true,
          opacity: 0.2
        });
        const wireframeMesh = new THREE.Mesh(wireframeGeo, wireframeMat);
        wireframeMesh.scale.set(scaleX, scaleY, scaleZ);
        wireframeMesh.position.set(0, 0, 0);
        wireframeMesh.name = 'volumeWireframe';
        scene.add(wireframeMesh);
        
        console.log('✅ Volume mesh added to scene at origin');
        console.log('Volume mesh scale:', volumeMesh.scale);
        console.log('Volume mesh position:', volumeMesh.position);
        console.log('✅ Wireframe helper added (green cube) with physical proportions');
        
        // Store volume scale for model matching
        window.volumeScale = { x: scaleX, y: scaleY, z: scaleZ };
        window.volumeUniformScale = baseScale; // Keep for backward compatibility
        
        // If model already loaded, scale it now
        if (modelGroup && window.modelOriginalBounds && window.loadedModel) {
          console.log('Model already exists, scaling to match volume...');
          scaleModelToMatchVolume();
        }
        
        // Store volume data for controls
        volumeData = { texture, material: volumeMaterial, dimensions, window_min, window_max };
        
        // Visualize detected regions if available
        if (spatial_metadata && spatial_metadata.detected_regions && spatial_metadata.detected_regions.length > 0) {
          visualizeDetectedRegions(
            spatial_metadata.detected_regions,
            { x: scaleX, y: scaleY, z: scaleZ },
            dimensions
          );
          // Show markers toggle
          document.getElementById('markersToggle').style.display = 'flex';
        }
        
        // Show volume controls in sidebar
        document.getElementById('volumeToggle').style.display = 'flex';
        document.getElementById('volumeLegend').style.display = 'flex';
        document.getElementById('opacitySection').style.display = 'block';
        
      } catch (error) {
        console.error('Failed to load volume data:', error);
      }
    }
    
    // Receive model URL and volume data from parent window
    window.addEventListener('message', (event) => {
      if (event.data && event.data.type === 'setModelData') {
        console.log('Received model data via postMessage');
        console.log('Event data keys:', Object.keys(event.data));
        
        // Check if volume data includes segmentation volumes
        if (event.data.volumeData && event.data.volumeData.segmentation_format === 'volume') {
          console.log('✅ Loading volume-based segmentation from volumeData');
          console.log('Segmentation dimensions:', event.data.volumeData.segmentation_dimensions);
          console.log('Pancreas voxels:', event.data.volumeData.pancreas_voxel_count);
          console.log('Tumor voxels:', event.data.volumeData.tumor_voxel_count);
          
          // Calculate scale factors from spatial metadata
          let segScaleX = 6, segScaleY = 6, segScaleZ = 6; // Default uniform scale
          
          if (event.data.volumeData.spatial_metadata && event.data.volumeData.spatial_metadata.resampling_transform) {
            const physicalSpacing = event.data.volumeData.spatial_metadata.resampling_transform.new_spacing;
            const segDims = event.data.volumeData.segmentation_dimensions;
            
            const physicalDimX = segDims[0] * physicalSpacing[0];
            const physicalDimY = segDims[1] * physicalSpacing[1];
            const physicalDimZ = segDims[2] * physicalSpacing[2];
            
            const maxDim = Math.max(physicalDimX, physicalDimY, physicalDimZ);
            segScaleX = (physicalDimX / maxDim) * 6;
            segScaleY = (physicalDimY / maxDim) * 6;
            segScaleZ = (physicalDimZ / maxDim) * 6;
            
            console.log('🎯 Segmentation volumes using physical scale:', [segScaleX, segScaleY, segScaleZ]);
          }
          
          // Create pancreas volume
          const pancreasTexture = createSegmentationTexture(
            event.data.volumeData.pancreas_volume,
            event.data.volumeData.segmentation_dimensions
          );
          
          const pancreasMaterial = new THREE.ShaderMaterial({
            uniforms: {
              segmentationTexture: { value: pancreasTexture },
              cameraPos: { value: camera.position },
              opacity: { value: 1.0 },
              segmentColor: { value: new THREE.Vector3(0.0, 1.0, 1.0) } // Cyan
            },
            vertexShader: segmentationVertexShader,
            fragmentShader: segmentationFragmentShader,
            side: THREE.DoubleSide,
            transparent: true,
            depthWrite: false,
            blending: THREE.NormalBlending,
            glslVersion: THREE.GLSL3
          });
          
          const pancreasGeometry = new THREE.BoxGeometry(1, 1, 1);
          pancreasVolumeMesh = new THREE.Mesh(pancreasGeometry, pancreasMaterial);
          pancreasVolumeMesh.name = 'pancreas_volume';
          pancreasVolumeMesh.scale.set(segScaleX, segScaleY, segScaleZ);
          pancreasVolumeMesh.position.set(0, 0, 0);
          scene.add(pancreasVolumeMesh);
          
          // Create tumor volume
          const tumorTexture = createSegmentationTexture(
            event.data.volumeData.tumor_volume,
            event.data.volumeData.segmentation_dimensions
          );
          
          const tumorMaterial = new THREE.ShaderMaterial({
            uniforms: {
              segmentationTexture: { value: tumorTexture },
              cameraPos: { value: camera.position },
              opacity: { value: 1.0 },
              segmentColor: { value: new THREE.Vector3(1.0, 0.0, 0.0) } // Red
            },
            vertexShader: segmentationVertexShader,
            fragmentShader: segmentationFragmentShader,
            side: THREE.DoubleSide,
            transparent: true,
            depthWrite: false,
            blending: THREE.NormalBlending,
            glslVersion: THREE.GLSL3
          });
          
          const tumorGeometry = new THREE.BoxGeometry(1, 1, 1);
          tumorVolumeMesh = new THREE.Mesh(tumorGeometry, tumorMaterial);
          tumorVolumeMesh.name = 'tumor_volume';
          tumorVolumeMesh.scale.set(segScaleX, segScaleY, segScaleZ);
          tumorVolumeMesh.position.set(0, 0, 0);
          scene.add(tumorVolumeMesh);
          
          console.log('✅ Segmentation volumes added to scene with physical proportions');
          
          // Load CT volume
          if (event.data.volumeData) {
            console.log('✅ Volume data included, loading...');
            loadVolumeData(event.data.volumeData);
          }
          
          // Hide loading
          loading.style.display = 'none';
        }
        // Fallback: Check if modelData has volume format
        else if (event.data.modelData && typeof event.data.modelData === 'object' && event.data.modelData.format === 'volume') {
          console.log('✅ Loading volume-based segmentation from modelData');
          console.log('Dimensions:', event.data.modelData.dimensions);
          console.log('Pancreas voxels:', event.data.modelData.pancreas_voxel_count);
          console.log('Tumor voxels:', event.data.modelData.tumor_voxel_count);
          
          // Create pancreas volume
          const pancreasTexture = createSegmentationTexture(
            event.data.modelData.pancreas_volume,
            event.data.modelData.dimensions
          );
          
          const pancreasMaterial = new THREE.ShaderMaterial({
            uniforms: {
              segmentationTexture: { value: pancreasTexture },
              cameraPos: { value: camera.position },
              opacity: { value: 1.0 },
              segmentColor: { value: new THREE.Vector3(0.0, 1.0, 1.0) } // Cyan
            },
            vertexShader: segmentationVertexShader,
            fragmentShader: segmentationFragmentShader,
            side: THREE.DoubleSide,
            transparent: true,
            depthWrite: false,
            blending: THREE.NormalBlending,
            glslVersion: THREE.GLSL3
          });
          
          const pancreasGeometry = new THREE.BoxGeometry(6, 6, 6);
          pancreasVolumeMesh = new THREE.Mesh(pancreasGeometry, pancreasMaterial);
          pancreasVolumeMesh.name = 'pancreas_volume';
          pancreasVolumeMesh.position.set(0, 0, 0);
          scene.add(pancreasVolumeMesh);
          
          // Create tumor volume
          const tumorTexture = createSegmentationTexture(
            event.data.modelData.tumor_volume,
            event.data.modelData.dimensions
          );
          
          const tumorMaterial = new THREE.ShaderMaterial({
            uniforms: {
              segmentationTexture: { value: tumorTexture },
              cameraPos: { value: camera.position },
              opacity: { value: 1.0 },
              segmentColor: { value: new THREE.Vector3(1.0, 0.0, 0.0) } // Red
            },
            vertexShader: segmentationVertexShader,
            fragmentShader: segmentationFragmentShader,
            side: THREE.DoubleSide,
            transparent: true,
            depthWrite: false,
            blending: THREE.NormalBlending,
            glslVersion: THREE.GLSL3
          });
          
          const tumorGeometry = new THREE.BoxGeometry(6, 6, 6);
          tumorVolumeMesh = new THREE.Mesh(tumorGeometry, tumorMaterial);
          tumorVolumeMesh.name = 'tumor_volume';
          tumorVolumeMesh.position.set(0, 0, 0);
          scene.add(tumorVolumeMesh);
          
          console.log('✅ Segmentation volumes added to scene');
          
          // Hide loading
          loading.style.display = 'none';
          
          // Load CT volume if provided
          if (event.data.volumeData) {
            console.log('✅ Volume data included, loading...');
            loadVolumeData(event.data.volumeData);
          }
        }
        // Fallback to mesh-based (old method)
        else {
          const modelDataUrl = typeof event.data.modelData === 'string' ? event.data.modelData : (event.data.modelData?.glb_fallback || event.data.modelData);
          
          if (!modelDataUrl) {
            console.error('❌ No modelData in message!');
            loading.innerHTML = '<div style="color: #EF4444;">❌ No model data received</div>';
            return;
          }
          
          console.log('⚠️ Using mesh fallback');
          console.log('Model data URL type:', typeof modelDataUrl);
          console.log('Model data URL starts with:', modelDataUrl.substring(0, 100));
          
          // Load the GLB model from data URL
          loadGLBModel(modelDataUrl);
          
          // Check if volume data is included
          if (event.data.volumeData) {
            console.log('✅ Volume data included, loading...');
            console.log('Volume data keys:', Object.keys(event.data.volumeData));
            loadVolumeData(event.data.volumeData);
          } else {
            console.log('⚠️ No volume data in message');
          }
        }
      }
    });
    
    function focusOnSegmentation() {
      // Check if volume-based segmentations exist
      if (pancreasVolumeMesh || tumorVolumeMesh) {
        console.log('Focusing on volume-based segmentation');
        
        // Since volumes are aligned, just zoom to the 6x6x6 cube center
        camera.position.set(4, 3, 4);
        camera.lookAt(0, 0, 0);
        controls.target.set(0, 0, 0);
        controls.minDistance = 2;
        controls.maxDistance = 15;
        controls.update();
        
        // Make CT volume very transparent to see segmentation better
        if (volumeMesh && volumeMesh.material.uniforms) {
          volumeMesh.material.uniforms.opacity.value = 0.05;
          const opacitySlider = document.getElementById('volumeOpacity');
          const opacityValue = document.getElementById('volumeOpacityValue');
          if (opacitySlider && opacityValue) {
            opacitySlider.value = 0.05;
            opacityValue.textContent = '0.05';
          }
        }
        
        console.log('✅ Focused on volume-based segmentation');
        return;
      }
      
      // Fallback to mesh-based segmentation
      if (!modelGroup) {
        console.log('No segmentation model loaded yet');
        alert('Please wait for the pancreas and tumor models to load first.');
        return;
      }
      
      // Calculate bounding box of segmentation meshes only
      const box = new THREE.Box3().setFromObject(modelGroup);
      const size = box.getSize(new THREE.Vector3());
      const center = box.getCenter(new THREE.Vector3());
      
      console.log('Segmentation bounding box:');
      console.log('  Center:', center);
      console.log('  Size:', size);
      
      // Calculate optimal camera distance
      const maxDim = Math.max(size.x, size.y, size.z);
      const fov = camera.fov * (Math.PI / 180);
      let cameraDistance = Math.abs(maxDim / Math.tan(fov / 2)) * 1.5;
      
      // Position camera at a good angle to view pancreas
      const direction = new THREE.Vector3(1, 0.5, 1).normalize();
      camera.position.copy(center).add(direction.multiplyScalar(cameraDistance));
      camera.lookAt(center);
      
      // Update controls target
      controls.target.copy(center);
      controls.minDistance = cameraDistance * 0.3;
      controls.maxDistance = cameraDistance * 3;
      controls.update();
      
      // Make volume very transparent to see segmentation better
      if (volumeMesh) {
        if (volumeMesh.material.uniforms) {
          volumeMesh.material.uniforms.opacity.value = 0.05;
        }
        // Update slider
        const opacitySlider = document.getElementById('volumeOpacity');
        const opacityValue = document.getElementById('volumeOpacityValue');
        if (opacitySlider && opacityValue) {
          opacitySlider.value = 0.05;
          opacityValue.textContent = '0.05';
        }
      }
      
      console.log('✅ Focused on segmentation');
      console.log('Camera position:', camera.position);
      console.log('Camera target:', controls.target);
      console.log('Camera distance:', cameraDistance);
    }
    
    function resetCamera() {
      camera.position.set(0, 1, 8);
      controls.target.set(0, 0, 0);
      
      // Reset volume opacity
      if (volumeMesh && volumeMesh.material.uniforms) {
        volumeMesh.material.uniforms.opacity.value = 0.15;
        const opacitySlider = document.getElementById('volumeOpacity');
        const opacityValue = document.getElementById('volumeOpacityValue');
        if (opacitySlider && opacityValue) {
          opacitySlider.value = 0.15;
          opacityValue.textContent = '0.15';
        }
      }
      
      controls.update();
      console.log('Camera reset');
    }
    
    // Stats panel toggle
    function toggleStats() {
      const infoPanel = document.getElementById('infoPanel');
      const statsButton = document.getElementById('statsButtonText');
      if (infoPanel.style.display === 'none') {
        infoPanel.style.display = 'block';
        statsButton.textContent = 'Hide Stats';
      } else {
        infoPanel.style.display = 'none';
        statsButton.textContent = 'Show Stats';
      }
    }
    
    // Update stats
    let lastTime = performance.now();
    let frames = 0;
    function updateStats() {
      frames++;
      const currentTime = performance.now();
      if (currentTime >= lastTime + 1000) {
        const fps = Math.round((frames * 1000) / (currentTime - lastTime));
        document.getElementById('fpsCount').textContent = fps;
        frames = 0;
        lastTime = currentTime;
      }
      
      // Update vertex/face count if model loaded
      if (modelGroup) {
        let totalVertices = 0;
        let totalFaces = 0;
        modelGroup.traverse((child) => {
          if (child.isMesh && child.geometry) {
            if (child.geometry.attributes.position) {
              totalVertices += child.geometry.attributes.position.count;
            }
            if (child.geometry.index) {
              totalFaces += child.geometry.index.count / 3;
            }
          }
        });
        document.getElementById('vertexCount').textContent = totalVertices.toLocaleString();
        document.getElementById('faceCount').textContent = Math.round(totalFaces).toLocaleString();
      }
    }
    
    // Setup UI controls
    function setupControls() {
      // Volume opacity
      const volumeOpacitySlider = document.getElementById('volumeOpacity');
      const volumeOpacityValue = document.getElementById('volumeOpacityValue');
      volumeOpacitySlider.addEventListener('input', (e) => {
        const value = parseFloat(e.target.value);
        volumeOpacityValue.textContent = value.toFixed(2);
        if (volumeMesh && volumeMesh.material.uniforms) {
          volumeMesh.material.uniforms.opacity.value = value;
        }
      });
      
      // Volume visibility toggle
      const showVolumeToggle = document.getElementById('showVolume');
      showVolumeToggle.addEventListener('change', (e) => {
        if (volumeMesh) {
          volumeMesh.visible = e.target.checked;
        }
        console.log('Volume visibility:', e.target.checked);
      });
      
      // Pancreas visibility toggle
      const showPancreasToggle = document.getElementById('showPancreas');
      showPancreasToggle.addEventListener('change', (e) => {
        if (pancreasVolumeMesh) {
          pancreasVolumeMesh.visible = e.target.checked;
        }
        // Also toggle mesh-based pancreas
        if (modelGroup) {
          modelGroup.traverse((child) => {
            if (child.name === 'pancreas') {
              child.visible = e.target.checked;
            }
          });
        }
        console.log('Pancreas visibility:', e.target.checked);
      });
      
      // Tumor visibility toggle
      const showTumorToggle = document.getElementById('showTumor');
      showTumorToggle.addEventListener('change', (e) => {
        if (tumorVolumeMesh) {
          tumorVolumeMesh.visible = e.target.checked;
        }
        // Also toggle mesh-based tumor
        if (modelGroup) {
          modelGroup.traverse((child) => {
            if (child.name === 'tumor') {
              child.visible = e.target.checked;
            }
          });
        }
        console.log('Tumor visibility:', e.target.checked);
      });
      
      // Markers visibility toggle
      const showMarkersToggle = document.getElementById('showMarkers');
      if (showMarkersToggle) {
        showMarkersToggle.addEventListener('change', (e) => {
          scene.children.forEach((child) => {
            if (child.name && (child.name.startsWith('region_marker_') || child.name.startsWith('region_bbox_'))) {
              child.visible = e.target.checked;
            }
          });
          console.log('Markers visibility:', e.target.checked);
        });
      }
      
      // Keyboard shortcuts
      document.addEventListener('keydown', (e) => {
        switch(e.key.toLowerCase()) {
          case 'r':
            resetCamera();
            break;
          case 'f':
            focusOnSegmentation();
            break;
          case 's':
            toggleStats();
            break;
        }
      });
      
      console.log('✅ UI controls setup complete');
    }
    
    // Initialize
    initThreeJS();
    console.log('3D Viewer initialized with Three.js, waiting for model data...');
    
    // Signal to parent window that we're ready
    if (window.opener) {
      window.opener.postMessage('viewerReady', '*');
      console.log('Sent viewerReady signal to parent');
    }
  </script>
</body>
</html>
    ''';
    
    // Open in new window
    final blob = html.Blob([htmlContent], 'text/html');
    final url = html.Url.createObjectUrlFromBlob(blob);
    
    _viewerWindow = html.window.open(
      url, 
      '3D Viewer',
      'width=1200,height=800,location=no,menubar=no,status=no,toolbar=no'
    );
    
    html.Url.revokeObjectUrl(url);
    
    // Listen for ready signal from the viewer window
    html.window.onMessage.listen((event) {
      if (event.data == 'viewerReady') {
        print('Viewer window is ready, sending model data...');
        if (_viewerWindow != null && !_viewerWindow!.closed!) {
          final Map<String, dynamic> message = {
            'type': 'setModelData',
            'modelData': modelSrc,
          };
          
          // Include volume data if available
          if (widget.volumeData != null) {
            message['volumeData'] = widget.volumeData;
            print('Including volume data in postMessage');
          }
          
          _viewerWindow!.postMessage(message, '*');
          print('Model data sent via postMessage');
        }
      }
    });
  }
  
  @override
  void dispose() {
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: AppTheme.surfaceCard,
      child: Container(
        width: 400,
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(
              Icons.open_in_new,
              color: AppTheme.accentTeal,
              size: 48,
            ),
            const SizedBox(height: 16),
            const Text(
              '3D Viewer Opened',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: AppTheme.textPrimary,
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              'The 3D visualization has opened in a new window using Three.js. '
              'Rotate, zoom, and explore the pancreas (cyan) and tumor (red) models.',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: AppTheme.textSecondary,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                TextButton(
                  onPressed: () {
                    _viewerWindow?.close();
                    Navigator.of(context).pop();
                  },
                  child: const Text('Close Both'),
                ),
                const SizedBox(width: 12),
                ElevatedButton(
                  onPressed: () => Navigator.of(context).pop(),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.primaryBlue,
                  ),
                  child: const Text('Keep Viewer Open'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
