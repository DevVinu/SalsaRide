class UserModel {
  final String id;
  final String email;
  final String fullName;
  final String? phone;
  final String role;
  final bool locationSharingEnabled;

  UserModel({
    required this.id,
    required this.email,
    required this.fullName,
    this.phone,
    required this.role,
    required this.locationSharingEnabled,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] ?? '',
      email: json['email'] ?? '',
      fullName: json['full_name'] ?? '',
      phone: json['phone'],
      role: json['role'] ?? 'DRIVER',
      locationSharingEnabled: json['location_sharing_enabled'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'full_name': fullName,
      'phone': phone,
      'role': role,
      'location_sharing_enabled': locationSharingEnabled,
    };
  }
}

