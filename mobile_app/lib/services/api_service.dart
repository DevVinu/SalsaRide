import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import '../models/user_model.dart';
import '../models/junction_model.dart';
import '../models/signal_model.dart';

class ApiService {
  String? _authToken;

  void setToken(String token) {
    _authToken = token;
  }

  Map<String, String> _headers() {
    final h = {'Content-Type': 'application/json'};
    if (_authToken != null) {
      h['Authorization'] = 'Bearer $_authToken';
    }
    return h;
  }

  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String fullName,
    String? phone,
  }) async {
    final res = await http.post(
      Uri.parse('${AppConfig.apiBaseUrl}/auth/register'),
      headers: _headers(),
      body: jsonEncode({
        'email': email,
        'password': password,
        'full_name': fullName,
        'phone': phone,
        'role': 'DRIVER',
        'location_sharing_enabled': true,
      }),
    );
    if (res.statusCode == 201) {
      return jsonDecode(res.body);
    }
    throw Exception(jsonDecode(res.body)['detail'] ?? 'Registration failed');
  }

  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    final res = await http.post(
      Uri.parse('${AppConfig.apiBaseUrl}/auth/login'),
      headers: _headers(),
      body: jsonEncode({'email': email, 'password': password}),
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception(jsonDecode(res.body)['detail'] ?? 'Login failed');
  }

  Future<List<JunctionModel>> getNearbyJunctions(double lat, double lon) async {
    final res = await http.get(
      Uri.parse('${AppConfig.apiBaseUrl}/junctions/nearby?latitude=$lat&longitude=$lon'),
      headers: _headers(),
    );
    if (res.statusCode == 200) {
      final List list = jsonDecode(res.body);
      return list.map((j) => JunctionModel.fromJson(j)).toList();
    }
    return [];
  }

  Future<Map<String, dynamic>> sendLocationPing({
    required String userId,
    required double latitude,
    required double longitude,
    required double speedKmh,
    bool isEmergency = false,
  }) async {
    final res = await http.post(
      Uri.parse('${AppConfig.apiBaseUrl}/traffic/ping'),
      headers: _headers(),
      body: jsonEncode({
        'user_id': userId,
        'latitude': latitude,
        'longitude': longitude,
        'speed_kmh': speedKmh,
        'is_emergency': isEmergency,
      }),
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception('Failed to send location ping');
  }

  Future<VirtualSignalModel> getSignalState(String junctionId) async {
    final res = await http.get(
      Uri.parse('${AppConfig.apiBaseUrl}/signals/$junctionId'),
      headers: _headers(),
    );
    if (res.statusCode == 200) {
      return VirtualSignalModel.fromJson(jsonDecode(res.body));
    }
    throw Exception('Failed to fetch signal state');
  }
}

