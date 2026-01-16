import 'package:flutter/material.dart';
import 'dart:html' as html;
import '../theme/app_theme.dart';

class Volume3DViewer extends StatefulWidget {
  final String gltfData;  // URL to GLB model
  final VoidCallback? onClose;
  
  const Volume3DViewer({
    super.key,
    required this.gltfData,
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
    final htmlContent = '''
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
    body {
      margin: 0;
      padding: 0;
      font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
      color: #E2E8F0;
      overflow: hidden;
    }
    .container {
      display: flex;
      flex-direction: column;
      height: 100vh;
    }
    .header {
      background: rgba(30, 41, 59, 0.95);
      padding: 20px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
      z-index: 10;
    }
    .title {
      font-size: 24px;
      font-weight: bold;
      margin: 0 0 10px 0;
      color: #06B6D4;
    }
    .legend {
      display: flex;
      gap: 20px;
      margin-top: 10px;
    }
    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .legend-box {
      width: 16px;
      height: 16px;
      border: 2px solid;
      border-radius: 3px;
    }
    .pancreas-color {
      border-color: #06B6D4;
      background: rgba(6, 182, 212, 0.3);
    }
    .tumor-color {
      border-color: #EF4444;
      background: rgba(239, 68, 68, 0.5);
    }
    .viewer-container {
      flex: 1;
      position: relative;
      min-height: 0;
    }
    #canvas3d {
      width: 100%;
      height: 100%;
      display: block;
    }
    .controls {
      background: rgba(30, 41, 59, 0.95);
      padding: 20px;
      box-shadow: 0 -4px 6px rgba(0, 0, 0, 0.3);
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 20px;
    }
    .control-group {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    button {
      background: #3B82F6;
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
      transition: background 0.2s;
    }
    button:hover {
      background: #2563EB;
    }
    .toggle {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    input[type="checkbox"] {
      width: 18px;
      height: 18px;
      cursor: pointer;
    }
    input[type="range"] {
      cursor: pointer;
    }
    .control-group label {
      white-space: nowrap;
      font-size: 14px;
    }
    .control-group span {
      min-width: 30px;
      text-align: right;
      font-size: 14px;
    }
    .loading {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      text-align: center;
      z-index: 100;
      background: rgba(30, 41, 59, 0.9);
      padding: 30px;
      border-radius: 10px;
    }
    .spinner {
      border: 3px solid rgba(6, 182, 212, 0.3);
      border-top: 3px solid #06B6D4;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      animation: spin 1s linear infinite;
      margin: 0 auto 15px;
    }
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    .instructions {
      background: rgba(59, 130, 246, 0.1);
      border: 1px solid rgba(59, 130, 246, 0.3);
      padding: 12px;
      border-radius: 6px;
      font-size: 13px;
      color: #94A3B8;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1 class="title">🔬 3D Pancreas & Tumor Visualization</h1>
      <div class="instructions">
        💡 <strong>Controls:</strong> Left-click + drag to rotate • Scroll to zoom • Right-click + drag to pan
      </div>
      <div class="legend">
        <div class="legend-item">
          <div class="legend-box pancreas-color"></div>
          <span>Pancreas Tissue</span>
        </div>
        <div class="legend-item">
          <div class="legend-box tumor-color"></div>
          <span>Tumor Regions</span>
        </div>
      </div>
    </div>
    
    <div class="viewer-container">
      <div class="loading" id="loading">
        <div class="spinner"></div>
        <div>Loading 3D model...</div>
      </div>
      
      <canvas id="canvas3d"></canvas>
    </div>
    
    <div class="controls">
      <div class="toggle">
        <input type="checkbox" id="autoRotate">
        <label for="autoRotate">Auto Rotate</label>
      </div>
      <div class="control-group" style="min-width: 200px;">
        <label for="lightIntensity">💡 Light:</label>
        <input type="range" id="lightIntensity" min="0" max="2" step="0.1" value="0.8" style="flex: 1;">
        <span id="lightValue">0.8</span>
      </div>
      <button onclick="resetCamera()">🔄 Reset Camera</button>
      <button onclick="window.close()">✅ Done</button>
    </div>
  </div>
  
  <script>
    const canvas = document.getElementById('canvas3d');
    const loading = document.querySelector('#loading');
    const autoRotateCheckbox = document.querySelector('#autoRotate');
    
    let scene, camera, renderer, controls, model, modelGroup;
    let autoRotateEnabled = false;
    let directionalLight, ambientLight;
    
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
      
      // Renderer
      renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
      renderer.setSize(canvas.clientWidth, canvas.clientHeight);
      renderer.setPixelRatio(window.devicePixelRatio);
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
      
      if (autoRotateEnabled && modelGroup) {
        modelGroup.rotation.y += 0.005;
      }
      
      controls.update();
      renderer.render(scene, camera);
    }
    
    function loadGLBModel(url) {
      console.log('Loading GLB from:', url);
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
          model.traverse((child) => {
            console.log('Child:', child.type, child.name, child);
            
            if (child.isMesh) {
              meshCount++;
              console.log('Found mesh:', child.name);
              console.log('  Geometry:', child.geometry);
              console.log('  Vertices:', child.geometry.attributes.position ? child.geometry.attributes.position.count : 0);
              console.log('  Material:', child.material);
              
              // Ensure mesh has a visible material
              if (!child.material || child.material.opacity === 0) {
                console.log('  Applying default material to mesh');
                child.material = new THREE.MeshStandardMaterial({
                  color: child.name.includes('tumor') ? 0xff0000 : 0x00ffff,
                  side: THREE.DoubleSide,
                  metalness: 0.3,
                  roughness: 0.7
                });
              }
              
              // Make sure it's visible
              child.visible = true;
              child.frustumCulled = false;
            }
          });
          
          console.log('Total meshes found:', meshCount);
          
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
          
          // Create a group to hold the model
          modelGroup = new THREE.Group();
          
          // Center model in the group
          model.position.set(-center.x, -center.y, -center.z);
          modelGroup.add(model);
          
          // Scale the group to make model bigger (5 units instead of 2)
          const maxDim = Math.max(size.x, size.y, size.z);
          if (maxDim > 0) {
            const scale = 5 / maxDim;  // Make it bigger!
            modelGroup.scale.setScalar(scale);
            console.log('Applied scale:', scale, 'to maxDim:', maxDim);
          }
          
          scene.add(modelGroup);
          
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
          const progress = (xhr.loaded / xhr.total) * 100;
          loading.innerHTML = '<div class="spinner"></div><div>Loading: ' + Math.round(progress) + '%</div>';
          console.log('Loading progress:', Math.round(progress) + '%');
        },
        function(error) {
          console.error('❌ Error loading GLB:', error);
          loading.innerHTML = '<div style="color: #EF4444;">❌ Failed to load model<br/><small>' + error.message + '</small></div>';
        }
      );
    }
    
    // Receive model URL from parent window
    window.addEventListener('message', (event) => {
      if (event.data && event.data.type === 'setModelData') {
        console.log('Received model data via postMessage');
        
        const modelUrl = 'http://localhost:8765/model.glb';
        console.log('Loading model from:', modelUrl);
        
        loadGLBModel(modelUrl);
      }
    });
    
    autoRotateCheckbox.addEventListener('change', (e) => {
      autoRotateEnabled = e.target.checked;
      console.log('Auto-rotate:', autoRotateEnabled);
    });
    
    // Light intensity slider
    const lightSlider = document.getElementById('lightIntensity');
    const lightValue = document.getElementById('lightValue');
    
    lightSlider.addEventListener('input', (e) => {
      const intensity = parseFloat(e.target.value);
      if (directionalLight) {
        directionalLight.intensity = intensity;
        lightValue.textContent = intensity.toFixed(1);
        console.log('Light intensity:', intensity);
      }
    });
    
    function resetCamera() {
      camera.position.set(0, 1, 3);
      controls.target.set(0, 0, 0);
      controls.update();
      console.log('Camera reset');
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
          _viewerWindow!.postMessage({
            'type': 'setModelData',
            'modelData': modelSrc,
          }, '*');
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
