# İleri Düzey Görüntü İşleme ve Graf Analizi

Bu bölüm, projenin temelindeki el izleme teknolojisini genişleten ileri düzey bilgisayarlı görü ve graf analizi konularını içerir.

---

## 🎯 YOLO (You Only Look Once)

YOLO, gerçek zamanlı nesne tespiti için kullanılan state-of-the-art bir derin öğrenme modelidir.

### Temel Özellikler

| Özellik | Açıklama |
|---------|----------|
| **Tek Geçiş** | Görüntüyü bir kez tarar, tüm nesneleri tespit eder |
| **Hız** | 45 FPS (YOLOv8 ile 120+ FPS) |
| **Sürümler** | YOLOv3, YOLOv4, YOLOv5, YOLOv8, YOLOv11 |

### Örnek: YOLOv8 ile Nesne Tespiti

```python
from ultralytics import YOLO
import cv2

# Model yükleme
model = YOLO('yolov8n.pt')  # nano versiyon (hızlı)

# Görüntü üzerinde tespit
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Tespit yap
    results = model(frame)
    
    # Sonuçları çiz
    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            conf = box.conf[0]
            cls = int(box.cls[0])
            
            # Sınırlayıcı kutu çiz
            cv2.rectangle(frame, 
                         (int(x1), int(y1)), 
                         (int(x2), int(y2)), 
                         (0, 255, 0), 2)
            
            # Etiket ekle
            label = f"{model.names[cls]} {conf:.2f}"
            cv2.putText(frame, label, 
                       (int(x1), int(y1)-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    
    cv2.imshow('YOLO Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### El Hareketi Projesi ile Entegrasyon

```python
# YOLO + MediaPipe kombinasyonu
from ultralytics import YOLO
import mediapipe as mp

class HybridDetector:
    def __init__(self):
        self.yolo = YOLO('yolov8n.pt')
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7
        )
    
    def detect(self, frame):
        # YOLO: Cisim tespiti
        yolo_results = self.yolo(frame, classes=[0])  # Sadece insan (class 0)
        
        # MediaPipe: El izleme
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hand_results = self.hands.process(rgb)
        
        return {
            'persons': yolo_results,
            'hands': hand_results
        }
```

### Bu Proje İçin Ne Anlama Gelir?

| Mevcut Durum | YOLO ile Eklenen Değer |
|--------------|----------------------|
| **MediaPipe Hands** sadece el izleme yapar | **YOLO** kişi tespiti + el izleme kombinasyonu |
| `web_app.py:215-356` generate_frames() döngüsü | Aynı döngüye YOLO inference eklenir |
| `is_hand_up()` fonksiyonu | `is_person_present()` kontrolü eklenebilir |

**Örnek Senaryo:**
```python
# generate_frames() içinde kullanım
def generate_frames():
    # ... mevcut kod ...
    
    # Yeni: YOLO ile önce kişi var mı kontrol et
    yolo_results = yolo_model(frame, classes=[0])  # Sadece insan
    if len(yolo_results[0].boxes) == 0:
        # Kimse yoksa, el izlemeyi atla
        continue
    
    # Mevcut: MediaPipe el izleme
    hand_results = hands.process(rgb_frame)
    # ... gerisi mevcut kod ...
```

**Fayda:** Kameraya kimse bakmadığında işlem gücü tasarrufu.

---

## 🔬 Detectron2 (Meta AI)

Facebook AI Research tarafından geliştirilen, nesne tespiti, segmentasyon ve poz tahmini için modüler bir platform.

### Detectron2 vs YOLO

| Kriter | Detectron2 | YOLO |
|--------|------------|------|
| **Hız** | Daha yavaş | Daha hızlı |
| **Doğruluk** | Daha yüksek (COCO'da) | İyi |
| **Esneklik** | Yüksek (custom backbone) | Orta |
| **Mask R-CNN** | Destekler | Desteklemez |
| **Kullanım** | Araştırma | Üretim |

### Örnek: Instance Segmentation

```python
import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog
import cv2

# Konfigürasyon
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file(
    "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"
))
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(
    "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"
)
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5

predictor = DefaultPredictor(cfg)

# Tahmin
im = cv2.imread("input.jpg")
outputs = predictor(im)

# Görselleştirme
v = Visualizer(im[:, :, ::-1], 
               MetadataCatalog.get(cfg.DATASETS.TRAIN[0]),
               scale=1.2)
out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
```

### Keypoint Detection (Pose Estimation)

```python
# COCO insan pozu tahmini
cfg.merge_from_file(model_zoo.get_config_file(
    "COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml"
))
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(
    "COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml"
)

predictor = DefaultPredictor(cfg)
outputs = predictor(image)

# 17 COCO keypoint: burun, gözler, omuzlar, dirsekler, bilekler, kalça, dizler, ayaklar
keypoints = outputs["instances"].pred_keypoints
```

### Bu Proje İçin Ne Anlama Gelir?

| Mevcut | Detectron2 Alternatifi |
|--------|----------------------|
| MediaPipe 21 noktalı **el landmark** | Detectron2 **tüm vücut pozu** (17 nokta) |
| `gestures.md` - sadece el hareketleri | Vücut dili kontrolü eklenebilir |
| `is_hand_up()` basit y karşılaştırması | Omuz-bilek açısı analizi |

**Kullanım Senaryosu:**
```python
# Detectron2 ile vücut pozu tespiti
cfg.merge_from_file(model_zoo.get_config_file(
    "COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml"
))
predictor = DefaultPredictor(cfg)

# Omuz ve bilek pozisyonuna göre kontrol
keypoints = outputs["instances"].pred_keypoints[0]
left_shoulder = keypoints[5]   # COCO index: omuz
left_wrist = keypoints[9]     # COCO index: bilek

# Kol kaldırma açısı hesaplama
if left_wrist[1] < left_shoulder[1]:  # y koordinatı (ters)
    status = "Kol kaldırıldı - Müzik çal"
```

**Ne Zaman Kullanılır:** Sadece el değil, tüm vücut hareketleriyle kontrol istendiğinde.

---

## 📐 P&ID Diyagram Analizi

P&ID (Piping and Instrumentation Diagram) gibi teknik çizimlerde şekil ve çizgi tespiti, endüstriyel otomasyon için kritik öneme sahiptir.

### Teknik Diyagram Analizi Akışı

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Girdi      │───→│  Ön İşlem │───→│  Çizgi      │───→│  Şekil      │
│  (PDF/IMG)  │    │  (Binarize) │    │  Tespiti    │    │  Tespiti     │
└─────────────┘    └─────────────┘    └─────────────┘    └──────┬──────┘
                                                                │
                                                                ▼
                                                       ┌─────────────────┐
                                                       │  Sembol         │
                                                       │  Sınıflandırma  │
                                                       │  (Valf, Pompa)  │
                                                       └─────────────────┘
```

### Çizgi Tespiti (Hough Transform)

```python
import cv2
import numpy as np

def detect_pipes(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Kenar tespiti
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # Hough Line Transform
    lines = cv2.HoughLinesP(
        edges, 
        rho=1, 
        theta=np.pi/180, 
        threshold=100,
        minLineLength=100,
        maxLineGap=10
    )
    
    # Çizgileri çiz
    result = img.copy()
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(result, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    return result

# Şekil tespiti (Kontur analizi)
def detect_symbols(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    
    contours, _ = cv2.findContours(
        thresh, 
        cv2.RETR_EXTERNAL, 
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    symbols = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 100:  # Gürültü filtreleme
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w)/h
            
            # Şekil sınıflandırma
            approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
            
            if len(approx) == 3:
                shape = "Valf (Üçgen)"
            elif len(approx) == 4:
                shape = "Tank (Dörtgen)"
            elif len(approx) > 8:
                shape = "Pompa (Daire)"
            else:
                shape = "Bilinmiyor"
            
            symbols.append({
                'shape': shape,
                'bbox': (x, y, w, h),
                'center': (x + w//2, y + h//2)
            })
    
    return symbols
```

### Template Matching ile Sembol Tanıma

```python
def match_symbols(image, templates):
    """
    templates: {'valve': valve_img, 'pump': pump_img, ...}
    """
    detections = []
    
    for symbol_name, template in templates.items():
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        locations = np.where(result >= threshold)
        
        for pt in zip(*locations[::-1]):
            detections.append({
                'symbol': symbol_name,
                'position': pt,
                'confidence': result[pt[1], pt[0]]
            })
    
    # Non-maximum suppression
    detections = nms(detections, threshold=0.5)
    return detections
```

### Bu Proje İçin Ne Anlama Gelir?

| Mevcut Proje | P&ID Tekniklerinin Uygulanması |
|--------------|------------------------------|
| `web_app.py:215-356` video işleme | Aynı OpenCV fonksiyonları kullanılır |
| El şekli tespiti (landmark) | **Kontur analizi** ile geometrik şekil tanıma |
| Basit y koordinatı karşılaştırması | **Hough Transform** ile çizgi/parmak yönü analizi |

**Entegrasyon Önerisi:**
```python
# mevcut is_hand_up() yerine gelişmiş versiyon
def detect_gesture_advanced(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    
    # Hough ile parmak çizgilerini tespit et
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, 
                           minLineLength=30, maxLineGap=10)
    
    if lines is not None:
        # Parmak yönü analizi
        vertical_lines = [l for l in lines 
                         if abs(l[0][3] - l[0][1]) > abs(l[0][2] - l[0][0])]
        if len(vertical_lines) >= 2:
            return "hand_up"
    
    return "no_gesture"
```

**Öğrenme:** P&ID'deki şekil tespiti, el izlemede alternatif bir yöntem olarak kullanılabilir.

---

## 🕸️ Neo4j (Graph Database)

Teknik diyagramlardaki ilişkileri modellemek için graf veritabanları idealdir. Neo4j, düğüm (node) ve ilişki (relationship) tabanlı bir veritabanıdır.

### P&ID Graf Modeli

```cypher
// Düğüm oluşturma
CREATE (p1:Pipe {id: 'P-101', type: 'Process', diameter: 100})
CREATE (p2:Pipe {id: 'P-102', type: 'Utility', diameter: 50})
CREATE (v1:Valve {id: 'V-201', type: 'Gate', size: 4})
CREATE (pump1:Pump {id: 'P-301', type: 'Centrifugal', power: 75})

// İlişkiler
CREATE (p1)-[:CONNECTS_TO {length: 10}]->(v1)
CREATE (v1)-[:CONTROLS]->(pump1)
CREATE (pump1)-[:OUTPUT_TO]->(p2)
```

### Python ile Neo4j Entegrasyonu

```python
from neo4j import GraphDatabase

class PidGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def add_component(self, component_type, properties):
        """
        component_type: 'Pipe', 'Valve', 'Pump', etc.
        properties: {'id': 'P-101', 'diameter': 100}
        """
        query = f"""
        CREATE (n:{component_type} $props)
        RETURN n
        """
        with self.driver.session() as session:
            return session.run(query, props=properties).single()
    
    def add_connection(self, from_id, to_id, rel_type, properties=None):
        query = f"""
        MATCH (a {{id: $from_id}}), (b {{id: $to_id}})
        CREATE (a)-[:{rel_type} $props]->(b)
        """
        with self.driver.session() as session:
            session.run(query, 
                       from_id=from_id, 
                       to_id=to_id,
                       props=properties or {})
    
    def find_path(self, start_id, end_id):
        """İki komponent arasındaki yolu bul"""
        query = """
        MATCH path = shortestPath(
            (a {id: $start_id})-[:CONNECTS_TO|OUTPUT_TO*]->(b {id: $end_id})
        )
        RETURN path
        """
        with self.driver.session() as session:
            result = session.run(query, start_id=start_id, end_id=end_id)
            return result.single()
    
    def get_downstream(self, component_id):
        """Bir komponentten sonraki tüm elemanları getir"""
        query = """
        MATCH (n {id: $id})-[:CONNECTS_TO|OUTPUT_TO*]->(downstream)
        RETURN collect(distinct downstream) as components
        """
        with self.driver.session() as session:
            result = session.run(query, id=component_id)
            return result.single()['components']
```

### Örnek: P&ID'den Graf Oluşturma

```python
import cv2
from neo4j import GraphDatabase

class PidToGraph:
    def __init__(self, neo4j_uri, user, password):
        self.graph = PidGraph(neo4j_uri, user, password)
    
    def process_diagram(self, image_path):
        # 1. Görüntü analizi
        img = cv2.imread(image_path)
        
        # 2. Sembol tespiti (Detectron2 veya template matching)
        symbols = self.detect_symbols(img)
        
        # 3. Çizgi tespiti
        lines = self.detect_lines(img)
        
        # 4. Graf oluştur
        for symbol in symbols:
            self.graph.add_component(
                symbol['type'], 
                {'id': symbol['id'], 'center': symbol['center']}
            )
        
        # 5. Bağlantıları ekle
        for line in lines:
            start_comp = self.find_nearest_component(line['start'], symbols)
            end_comp = self.find_nearest_component(line['end'], symbols)
            
            if start_comp and end_comp:
                self.graph.add_connection(
                    start_comp['id'], 
                    end_comp['id'],
                    'CONNECTS_TO',
                    {'length': line['length']}
                )
        
        return f"{len(symbols)} komponent, {len(lines)} bağlantı eklendi"
```

### Bu Proje İçin Ne Anlama Gelir?

| Mevcut | Neo4j Entegrasyonu |
|--------|-------------------|
| `settings.json` basit JSON yapılandırması | **Graf veritabanı** ile gesture ilişkileri modelleme |
| `state{}` dict runtime bellekte | **Kalıcı graf** - öğrenilen gesture pattern'leri |
| Tek kullanıcı | Kullanıcı-gesture ilişkileri ağı |

**Gesture Öğrenme Sistemi:**
```cypher
// Kullanıcı ve gesture ilişkisi
CREATE (u:User {id: 'user_1', name: 'Ahmet'})
CREATE (g1:Gesture {type: 'hand_up', action: 'play'})
CREATE (g2:Gesture {type: 'fist', action: 'stop'})

// Kullanım pattern'leri
CREATE (u)-[:USES {frequency: 45, last_used: datetime()}]->(g1)
CREATE (u)-[:USES {frequency: 12, last_used: datetime()}]->(g2)

// En çok kullanılan gesture'ı sorgula
MATCH (u:User)-[r:USES]->(g)
WHERE u.id = 'user_1'
RETURN g.type, r.frequency
ORDER BY r.frequency DESC
```

**Python Entegrasyonu:**
```python
# web_app.py içinde
class GestureLearningSystem:
    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver
    
    def record_gesture(self, user_id, gesture_type):
        with self.driver.session() as session:
            session.run("""
                MATCH (u:User {id: $user})
                MATCH (g:Gesture {type: $gesture})
                MERGE (u)-[r:USES]->(g)
                SET r.frequency = coalesce(r.frequency, 0) + 1,
                    r.last_used = datetime()
            """, user=user_id, gesture=gesture_type)
    
    def get_favorite_gesture(self, user_id):
        # En çok kullanılan gesture'ı döndür
        # UI'da öneri olarak göster
        pass
```

**Fayda:** Kullanıcı davranışlarını analiz edip kişiselleştirilmiş deneyim.

---

## 📊 NetworkX (Python Graph Library)

Neo4j'e alternatif olarak yerel Python analizi için NetworkX kullanılabilir.

### NetworkX Temelleri

```python
import networkx as nx
import matplotlib.pyplot as plt

# Graf oluştur
G = nx.DiGraph()  # Yönlü graf

# Düğüm ekle
G.add_node('P-101', type='Pipe', diameter=100)
G.add_node('V-201', type='Valve', size=4)
G.add_node('Pump-301', type='Pump', power=75)

# Kenar ekle
G.add_edge('P-101', 'V-201', weight=10, relation='connects')
G.add_edge('V-201', 'Pump-301', weight=5, relation='controls')

# Analiz
print(f"Düğüm sayısı: {G.number_of_nodes()}")
print(f"Kenar sayısı: {G.number_of_edges()}")

# Yol bulma
path = nx.shortest_path(G, 'P-101', 'Pump-301', weight='weight')
print(f"En kısa yol: {path}")

# Görselleştirme
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue')
labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
plt.show()
```

### P&ID Network Analizi

```python
class PidNetworkAnalyzer:
    def __init__(self):
        self.G = nx.DiGraph()
    
    def add_pipeline(self, components, connections):
        """
        components: [{'id': 'P-101', 'type': 'Pipe'}, ...]
        connections: [('P-101', 'V-201'), ...]
        """
        for comp in components:
            self.G.add_node(comp['id'], **comp)
        
        for conn in connections:
            self.G.add_edge(conn[0], conn[1])
    
    def find_critical_paths(self):
        """Kritik boru hatlarını bul"""
        # En uzun yollar
        all_paths = []
        sources = [n for n in self.G.nodes() if self.G.in_degree(n) == 0]
        sinks = [n for n in self.G.nodes() if self.G.out_degree(n) == 0]
        
        for source in sources:
            for sink in sinks:
                try:
                    paths = list(nx.all_simple_paths(self.G, source, sink))
                    all_paths.extend(paths)
                except nx.NetworkXNoPath:
                    continue
        
        return sorted(all_paths, key=len, reverse=True)
    
    def detect_loops(self):
        """Döngüleri tespit et (tasıma hatları için önemli)"""
        try:
            cycles = list(nx.simple_cycles(self.G))
            return cycles
        except:
            return []
    
    def component_dependencies(self, component_id):
        """Bir komponente bağımlı tüm elemanları bul"""
        descendants = nx.descendants(self.G, component_id)
        return list(descendants)
    
    def calculate_flow_capacity(self):
        """Maksimum akış kapasitesi analizi"""
        # Kenar kapasitelerini diameter'a göre hesapla
        for u, v, data in self.G.edges(data=True):
            u_diam = self.G.nodes[u].get('diameter', 50)
            v_diam = self.G.nodes[v].get('diameter', 50)
            capacity = min(u_diam, v_diam) * 0.5  # Basit formül
            data['capacity'] = capacity
        
        return nx.maximum_flow_value(
            self.G.to_undirected(),
            [n for n in self.G.nodes() if self.G.in_degree(n) == 0][0],
            [n for n in self.G.nodes() if self.G.out_degree(n) == 0][0]
        )
```

### Neo4j ↔ NetworkX Dönüşümü

```python
def neo4j_to_networkx(driver):
    """Neo4j veritabanını NetworkX grafına dönüştür"""
    G = nx.DiGraph()
    
    with driver.session() as session:
        # Düğümleri al
        nodes = session.run("MATCH (n) RETURN n")
        for record in nodes:
            node = record['n']
            G.add_node(
                node['id'],
                labels=list(node.labels),
                **dict(node)
            )
        
        # İlişkileri al
        rels = session.run("MATCH ()-[r]->() RETURN r")
        for record in rels:
            rel = record['r']
            start = rel.start_node['id']
            end = rel.end_node['id']
            G.add_edge(start, end, type=rel.type, **dict(rel))
    
    return G

def networkx_to_neo4j(G, driver):
    """NetworkX grafını Neo4j'ye aktar"""
    with driver.session() as session:
        # Düğümleri oluştur
        for node_id, data in G.nodes(data=True):
            labels = ':'.join(data.get('labels', ['Node']))
            props = {k: v for k, v in data.items() if k != 'labels'}
            
            query = f"""
            CREATE (n:{labels} {{id: $id}})
            SET n += $props
            """
            session.run(query, id=node_id, props=props)
        
        # İlişkileri oluştur
        for u, v, data in G.edges(data=True):
            rel_type = data.get('type', 'RELATED_TO')
            props = {k: v for k, v in data.items() if k != 'type'}
            
            query = f"""
            MATCH (a {{id: $from}}), (b {{id: $to}})
            CREATE (a)-[:{rel_type} $props]->(b)
            """
            session.run(query, from=u, to=v, props=props)
```

### Bu Proje İçin Ne Anlama Gelir?

| Mevcut | NetworkX Analizi |
|--------|------------------|
| `is_hand_up()` → `is_fist()` bağımsız fonksiyonlar | **Gesture geçiş grafı** - hangi gesture'dan hangisine geçilir |
| `status` JSON anlık durum | **Geçmiş durum zinciri** analizi |
| Tekil threshold değerleri | Optimal threshold'u graf analizi ile bulma |

**Gesture Geçiş Analizi:**
```python
# web_app.py içinde state yönetimi
import networkx as nx

class GestureTransitionAnalyzer:
    def __init__(self):
        self.G = nx.DiGraph()
        self.current_state = 'idle'
    
    def record_transition(self, from_gesture, to_gesture):
        """Gesture geçişini kaydet"""
        if not self.G.has_edge(from_gesture, to_gesture):
            self.G.add_edge(from_gesture, to_gesture, weight=0)
        
        self.G[from_gesture][to_gesture]['weight'] += 1
    
    def get_most_likely_next(self, current_gesture):
        """Mevcut gesture'dan sonra en olası sonraki gesture"""
        if current_gesture not in self.G:
            return None
        
        successors = dict(self.G[current_gesture])
        if not successors:
            return None
        
        return max(successors.items(), key=lambda x: x[1]['weight'])[0]
    
    def detect_anomaly(self, gesture_sequence):
        """Sıra dışı gesture pattern'ini tespit et"""
        # Normal yol: hand_up → hand_down → fist
        # Anomali: hand_up → fist (direkt durdurma - kaza?)
        try:
            path = nx.shortest_path(self.G, gesture_sequence[0], gesture_sequence[-1])
            return len(path) < len(gesture_sequence)  # Kısayol kullanıldı
        except nx.NetworkXNoPath:
            return True  # Anormal - hiç görülmemiş geçiş

# Kullanım
gesture_graph = GestureTransitionAnalyzer()

# generate_frames() içinde
def on_gesture_detected(gesture):
    global last_gesture
    
    if last_gesture != gesture:
        gesture_graph.record_transition(last_gesture, gesture)
        
        # Tahmin yap
        predicted = gesture_graph.get_most_likely_next(gesture)
        if predicted:
            print(f"Sonraki olası gesture: {predicted}")
    
    last_gesture = gesture
```

**Fayda:** Kullanıcı alışkanlıklarını öğrenip öngörücü kontrol.

---

## 🤖 Multi-Agent Sistemler

Teknik diyagram analizi ve süreç kontrolü için çoklu ajan (multi-agent) mimarisi.

### Multi-Agent Mimarisi

```
┌─────────────────────────────────────────────────────────────────┐
│                     Coordinator Agent                           │
│                    (Merkezi Koordinatör)                        │
└──────────┬──────────────┬──────────────┬──────────────┬─────────┘
           │              │              │              │
     ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐  ┌────▼────┐
     │ Detection │  │  Analysis │  │  Graph    │  │ Control  │
     │ Agent     │  │  Agent    │  │  Agent    │  │ Agent    │
     │ (Görüntü) │  │  (Şekil)  │  │  (Neo4j)  │  │ (Aksiyon)│
     └───────────┘  └───────────┘  └───────────┘  └──────────┘
```

### Python ile Multi-Agent Implementasyonu

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any
import threading
import queue
import time

class BaseAgent(ABC):
    """Tüm ajanların temel sınıfı"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.inbox = queue.Queue()
        self.outbox = queue.Queue()
        self.running = False
        self.thread = None
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
    
    def send_message(self, to_agent: str, message: Dict):
        """Başka bir ajana mesaj gönder"""
        msg = {
            'from': self.agent_id,
            'to': to_agent,
            'content': message,
            'timestamp': time.time()
        }
        # Coordinator'a ilet
        CoordinatorAgent.instance.route_message(msg)
    
    @abstractmethod
    def run(self):
        """Ana ajan döngüsü - alt sınıflar implemente etmeli"""
        pass
    
    @abstractmethod
    def process_message(self, message: Dict):
        """Gelen mesajları işle"""
        pass

class DetectionAgent(BaseAgent):
    """Görüntü tespiti ajanı - YOLO/MediaPipe kullanır"""
    
    def __init__(self):
        super().__init__('detection')
        from ultralytics import YOLO
        self.model = YOLO('yolov8n.pt')
        self.camera = None
    
    def run(self):
        import cv2
        self.camera = cv2.VideoCapture(0)
        
        while self.running:
            ret, frame = self.camera.read()
            if not ret:
                continue
            
            # Nesne tespiti
            results = self.model(frame)
            
            # Sonuçları mesaj olarak gönder
            detections = []
            for result in results:
                for box in result.boxes:
                    detections.append({
                        'class': result.names[int(box.cls[0])],
                        'confidence': float(box.conf[0]),
                        'bbox': box.xyxy[0].tolist()
                    })
            
            if detections:
                self.send_message('analysis', {
                    'type': 'detections',
                    'data': detections,
                    'frame_id': int(time.time() * 1000)
                })
            
            # Mesaj kontrolü
            try:
                msg = self.inbox.get(timeout=0.1)
                self.process_message(msg)
            except queue.Empty:
                pass
        
        self.camera.release()
    
    def process_message(self, message):
        if message.get('command') == 'change_camera':
            # Kamera değiştir
            pass

class AnalysisAgent(BaseAgent):
    """Şekil analizi ajanı - Tespit edilen nesneleri analiz eder"""
    
    def __init__(self):
        super().__init__('analysis')
        self.detected_objects = []
    
    def run(self):
        while self.running:
            try:
                msg = self.inbox.get(timeout=0.1)
                self.process_message(msg)
            except queue.Empty:
                continue
    
    def process_message(self, message):
        content = message.get('content', {})
        
        if content.get('type') == 'detections':
            detections = content.get('data', [])
            
            # Analiz yap
            analysis = self.analyze_objects(detections)
            
            # Sonuçları Graph Agent'a gönder
            self.send_message('graph', {
                'type': 'object_analysis',
                'data': analysis
            })
    
    def analyze_objects(self, detections):
        """Nesneler arası ilişkileri analiz et"""
        analysis = {
            'count': len(detections),
            'categories': {},
            'relationships': []
        }
        
        for det in detections:
            cls = det['class']
            analysis['categories'][cls] = analysis['categories'].get(cls, 0) + 1
        
        # Yakınlık analizi
        for i, det1 in enumerate(detections):
            for det2 in detections[i+1:]:
                dist = self.calculate_distance(det1['bbox'], det2['bbox'])
                if dist < 100:  # Pixel threshold
                    analysis['relationships'].append({
                        'from': det1['class'],
                        'to': det2['class'],
                        'distance': dist,
                        'type': 'proximity'
                    })
        
        return analysis
    
    def calculate_distance(self, bbox1, bbox2):
        import math
        c1 = ((bbox1[0] + bbox1[2]) / 2, (bbox1[1] + bbox1[3]) / 2)
        c2 = ((bbox2[0] + bbox2[2]) / 2, (bbox2[1] + bbox2[3]) / 2)
        return math.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2)

class GraphAgent(BaseAgent):
    """Graf yönetimi ajanı - Neo4j ile entegre"""
    
    def __init__(self, neo4j_uri, user, password):
        super().__init__('graph')
        from neo4j import GraphDatabase
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(user, password))
    
    def run(self):
        while self.running:
            try:
                msg = self.inbox.get(timeout=0.1)
                self.process_message(msg)
            except queue.Empty:
                continue
    
    def process_message(self, message):
        content = message.get('content', {})
        
        if content.get('type') == 'object_analysis':
            data = content.get('data', {})
            
            # Grafı güncelle
            self.update_graph(data)
            
            # Control Agent'a durum raporu
            self.send_message('control', {
                'type': 'graph_update',
                'status': 'updated',
                'object_count': data.get('count', 0)
            })
    
    def update_graph(self, analysis):
        with self.driver.session() as session:
            # Mevcut nesneleri temizle (opsiyonel)
            # session.run("MATCH (n:Detected) DELETE n")
            
            # Yeni nesneleri ekle
            for cat, count in analysis.get('categories', {}).items():
                session.run("""
                    MERGE (n:Detected {category: $cat})
                    SET n.count = $count,
                        n.timestamp = datetime()
                """, cat=cat, count=count)
            
            # İlişkileri ekle
            for rel in analysis.get('relationships', []):
                session.run("""
                    MATCH (a:Detected {category: $from}),
                          (b:Detected {category: $to})
                    MERGE (a)-[r:RELATED_TO]->(b)
                    SET r.distance = $dist,
                        r.type = $type
                """, from=rel['from'], to=rel['to'], 
                     dist=rel['distance'], type=rel['type'])

class ControlAgent(BaseAgent):
    """Kontrol ajanı - Kararlar alır ve eylemler gerçekleştirir"""
    
    def __init__(self):
        super().__init__('control')
        self.music_controller = None  # Mevcut projedeki müzik kontrolü
    
    def run(self):
        while self.running:
            try:
                msg = self.inbox.get(timeout=0.1)
                self.process_message(msg)
            except queue.Empty:
                continue
    
    def process_message(self, message):
        content = message.get('content', {})
        
        if content.get('type') == 'graph_update':
            count = content.get('object_count', 0)
            
            # Karar mantığı
            if count > 5:
                self.trigger_action('high_activity')
            elif count == 0:
                self.trigger_action('no_activity')
    
    def trigger_action(self, scenario):
        if scenario == 'high_activity':
            print("[ControlAgent] Yoğun aktivite tespit edildi!")
            # Müzik hızını artır veya başka bir aksiyon
        elif scenario == 'no_activity':
            print("[ControlAgent] Aktivite yok")

class CoordinatorAgent:
    """Merkezi koordinatör - Singleton pattern"""
    instance = None
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.message_history = []
    
    def register_agent(self, agent: BaseAgent):
        self.agents[agent.agent_id] = agent
    
    def route_message(self, message):
        """Mesajı hedef ajana ilet"""
        to_agent = message.get('to')
        if to_agent in self.agents:
            self.agents[to_agent].inbox.put(message)
            self.message_history.append(message)
    
    def start_all(self):
        for agent in self.agents.values():
            agent.start()
    
    def stop_all(self):
        for agent in self.agents.values():
            agent.stop()
```

### Multi-Agent Sistem Kullanımı

```python
# Sistem başlatma
def main():
    # Koordinatör oluştur
    coordinator = CoordinatorAgent()
    CoordinatorAgent.instance = coordinator
    
    # Ajanları oluştur ve kaydet
    detection = DetectionAgent()
    analysis = AnalysisAgent()
    graph = GraphAgent("bolt://localhost:7687", "neo4j", "password")
    control = ControlAgent()
    
    coordinator.register_agent(detection)
    coordinator.register_agent(analysis)
    coordinator.register_agent(graph)
    coordinator.register_agent(control)
    
    # Sistem başlat
    coordinator.start_all()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nSistem durduruluyor...")
        coordinator.stop_all()

if __name__ == '__main__':
    main()
```

### Bu Proje İçin Ne Anlama Gelir?

| Mevcut | Multi-Agent Mimarisine Dönüşüm |
|--------|-------------------------------|
| `web_app.py` - monolitik Flask uygulaması | **Ajan tabanlı** dağıtık mimari |
| `generate_frames()` tek thread | Her görev için **özel ajan** |
| Sıralı işlem: kamera → MediaPipe → gesture → müzik | **Paralel async** ajan iletişimi |

**Mevcut Kodun Ajanlara Bölünmesi:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CoordinatorAgent (Flask App)                   │
│                    - HTTP endpoint'leri yönetir                   │
└──────────┬──────────────┬──────────────┬──────────────┬─────────┘
           │              │              │              │
     ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐  ┌────▼────┐
     │ Camera    │  │ MediaPipe │  │  Gesture  │  │ Music   │
     │ Agent     │  │ Agent     │  │  Agent    │  │ Agent   │
     │ (cv2)     │  │ (el izleme│  │ (karar)   │  │ (ffplay)│
     └───────────┘  └───────────┘  └───────────┘  └─────────┘
```

**Mevcut `generate_frames()` fonksiyonunun ajanlara bölünmesi:**

```python
# MEVCUT KOD (web_app.py:215-356)
def generate_frames():
    while state['camera_on']:
        ret, frame = cap.read()  # → CameraAgent
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)  # → MediaPipeAgent
        
        if results.multi_hand_landmarks:
            landmarks = results.multi_hand_landmarks[0]
            hand_up = is_hand_up(landmarks)  # → GestureAgent
            if hand_up:
                _play_music()  # → MusicAgent

# MULTI-AGENT VERSİYONU
class CameraAgent(BaseAgent):
    def run(self):
        cap = cv2.VideoCapture(0)
        while self.running:
            ret, frame = cap.read()
            if ret:
                self.send_message('mediapipe', {'frame': frame})

class MediaPipeAgent(BaseAgent):
    def __init__(self):
        super().__init__('mediapipe')
        self.hands = mp.solutions.hands.Hands()
    
    def process_message(self, msg):
        frame = msg['content']['frame']
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        
        if results.multi_hand_landmarks:
            self.send_message('gesture', {
                'landmarks': results.multi_hand_landmarks[0]
            })

class GestureAgent(BaseAgent):
    def process_message(self, msg):
        landmarks = msg['content']['landmarks']
        
        if is_hand_up(landmarks):
            self.send_message('music', {'action': 'play'})
        elif is_fist(landmarks):
            self.send_message('music', {'action': 'stop'})

class MusicAgent(BaseAgent):
    def __init__(self):
        super().__init__('music')
        self.current_proc = None
    
    def process_message(self, msg):
        action = msg['content']['action']
        if action == 'play':
            self._play()
        elif action == 'stop':
            self._stop()
```

**Neden Multi-Agent?**

| Problem | Mevcut Çözüm | Multi-Agent Çözümü |
|---------|-------------|-------------------|
| Kamera yavaşlar, müzik kesilir | Tek thread bloke olur | CameraAgent bağımsız çalışır |
| Yeni gesture eklemek zor | `generate_frames()` içinde değişiklik | Yeni GestureAgent ekle |
| Test zorluğu | Entegre test gerekir | Her ajan bağımsız test edilir |
| Ölçeklenebilirlik | Monolitik limit | Ajanlar farklı makinelere dağıtılabilir |

**Sonuç:** Mevcut proje basit ve işlevsel. Multi-Agent karmaşıklık getirir ama ölçeklenebilirlik sağlar.

---

## 📚 Özet Tablo

| Teknoloji | Kullanım Alanı | Öğrenme Eğrisi | Performans |
|-----------|----------------|----------------|------------|
| **YOLO** | Gerçek zamanlı nesne tespiti | Orta | Çok Hızlı |
| **Detectron2** | Araştırma, karmaşık segmentasyon | Yüksek | Orta |
| **OpenCV Hough** | Teknik çizgi tespiti | Düşük | Hızlı |
| **Neo4j** | İlişkisel veri modelleme | Orta | Bağımlı |
| **NetworkX** | Yerel graf analizi | Düşük | Hızlı |
| **Multi-Agent** | Dağıtık sistemler | Yüksek | Ölçeklenebilir |

---

## � Mevcut Proje ile Karşılaştırma

### Ne Kullanılıyor? Ne Eklenebilir?

| Mevcut Bileşen | Dosya/Satır | Alternatif/Genişletme | Fayda |
|----------------|-------------|----------------------|-------|
| **MediaPipe Hands** | `web_app.py:215-356` | **YOLO** + MediaPipe | Kişi var/yok kontrolü |
| **21 Landmark** | `landmarks.md` | **Detectron2** (17 keypoint) | Vücut dili kontrolü |
| **Basit threshold** | `is_hand_up():191-193` | **P&ID Hough Transform** | Parmak yönü analizi |
| **settings.json** | `settings.json` | **Neo4j** graf veritabanı | Kullanıcı öğrenme sistemi |
| **state dict** | `state{} bellekte` | **NetworkX** graf analizi | Gesture geçiş tahmini |
| **Monolitik Flask** | `web_app.py` | **Multi-Agent** mimari | Ölçeklenebilirlik |

### Entegrasyon Zorluk Seviyeleri

```
Kolay ──────────────────────────────────────────────> Zor

[P&ID Teknikleri]  [NetworkX]  [YOLO]  [Neo4j]  [Detectron2]  [Multi-Agent]
     │                │          │        │          │             │
     └─ Aynı OpenCV   └─ Sadece   └─ Pip   └─ DB    └─ GPU       └─ Mimari
        fonksiyonlar   Python      install  kurulumu gerekli      değişikliği
        kullanılır     kütüphanesi
```

### Tavsiye Edilen Geliştirme Yolu

**Aşama 1 (Kolay):** P&ID tekniklerini deneyin
- `is_hand_up()` fonksiyonunu Hough Transform ile geliştirin
- Kontur analizi ekleyin

**Aşama 2 (Orta):** NetworkX ile gesture analizi
- Kullanıcı geçiş pattern'lerini öğrenin
- `thresholds.md` değerlerini dinamik yapın

**Aşama 3 (İleri):** YOLO veya Neo4j
- Kişi tespiti (YOLO) veya kullanıcı profili (Neo4j)

**Aşama 4 (Uzman):** Multi-Agent mimarisi
- Sadece yüksek ölçeklenebilirlik gerektiğinde

---

## �🔗 Faydalı Kaynaklar

- [YOLOv8 Dokümantasyonu](https://docs.ultralytics.com/)
- [Detectron2 GitHub](https://github.com/facebookresearch/detectron2)
- [Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)
- [NetworkX Dokümantasyonu](https://networkx.org/documentation/stable/)
- [Multi-Agent Systems - MESA Framework](https://mesa.readthedocs.io/)
