class JunctionModel {
  final String id;
  final String junctionCode;
  final String name;
  final String city;
  final String address;
  final double latitude;
  final double longitude;
  final int detectionRadiusMeters;
  final int innerZoneMeters;
  final int midZoneMeters;
  final double? distanceToUserMeters;
  final bool? isInsideDetectionZone;

  JunctionModel({
    required this.id,
    required this.junctionCode,
    required this.name,
    required this.city,
    required this.address,
    required this.latitude,
    required this.longitude,
    required this.detectionRadiusMeters,
    required this.innerZoneMeters,
    required this.midZoneMeters,
    this.distanceToUserMeters,
    this.isInsideDetectionZone,
  });

  factory JunctionModel.fromJson(Map<String, dynamic> json) {
    return JunctionModel(
      id: json['id'] ?? '',
      junctionCode: json['junction_code'] ?? '',
      name: json['name'] ?? '',
      city: json['city'] ?? '',
      address: json['address'] ?? '',
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      detectionRadiusMeters: json['detection_radius_meters'] ?? 500,
      innerZoneMeters: json['inner_zone_meters'] ?? 150,
      midZoneMeters: json['mid_zone_meters'] ?? 300,
      distanceToUserMeters: json['distance_to_user_meters'] != null
          ? (json['distance_to_user_meters'] as num).toDouble()
          : null,
      isInsideDetectionZone: json['is_inside_detection_zone'],
    );
  }
}

