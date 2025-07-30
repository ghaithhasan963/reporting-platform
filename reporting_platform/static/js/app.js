const points = {{ heat_data | safe }};
L.heatLayer(points, { radius: 25 }).addTo(map);
function showNearbyAlert(text) {
    alert(text); // ممكن نستخدم Toast لاحقاً
}
