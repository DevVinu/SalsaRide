import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import '../models/junction_model.dart';
import '../services/api_service.dart';
import '../services/location_service.dart';

class JunctionProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();
  final LocationService _locationService = LocationService();

  List<JunctionModel> _nearbyJunctions = [];
  JunctionModel? _selectedJunction;
  Position? _currentPosition;
  bool _isLoading = false;
  bool _isTrackingGps = false;
  Map<String, dynamic>? _currentAdvisory;
  String? _gpsStatusMessage;

  List<JunctionModel> get nearbyJunctions => _nearbyJunctions;
  JunctionModel? get selectedJunction => _selectedJunction;
  Position? get currentPosition => _currentPosition;
  bool get isLoading => _isLoading;
  bool get isTrackingGps => _isTrackingGps;
  Map<String, dynamic>? get currentAdvisory => _currentAdvisory;
  String? get gpsStatusMessage => _gpsStatusMessage;

  Future<void> fetchLocationAndJunctions() async {
    _isLoading = true;
    notifyListeners();

    _currentPosition = await _locationService.getCurrentPosition();
    if (_currentPosition != null) {
      _nearbyJunctions = await _apiService.getNearbyJunctions(
        _currentPosition!.latitude,
        _currentPosition!.longitude,
      );
      if (_nearbyJunctions.isNotEmpty && _selectedJunction == null) {
        _selectedJunction = _nearbyJunctions.first;
      }
    }

    _isLoading = false;
    notifyListeners();
  }

  void selectJunction(JunctionModel junction) {
    _selectedJunction = junction;
    notifyListeners();
  }

  void startLiveGpsTracking(String userId) {
    if (_isTrackingGps) return;
    _isTrackingGps = true;
    _gpsStatusMessage = "Starting GPS stream...";
    notifyListeners();

    _locationService.startPositionStream((Position pos) async {
      _currentPosition = pos;
      try {
        final speedKmh = pos.speed >= 0 ? pos.speed * 3.6 : 0.0;
        final res = await _apiService.sendLocationPing(
          userId: userId,
          latitude: pos.latitude,
          longitude: pos.longitude,
          speedKmh: speedKmh,
        );

        if (res['status'] == 'IN_ZONE') {
          _gpsStatusMessage = "Approaching ${res['junction_name']} (${res['observation']['corridor']})";
          _currentAdvisory = res['advisory'];
        } else {
          _gpsStatusMessage = "GPS active: Outside junction perimeter";
          _currentAdvisory = null;
        }
      } catch (e) {
        _gpsStatusMessage = "GPS error: ${e.toString()}";
      }
      notifyListeners();
    });
  }

  void stopLiveGpsTracking() {
    _locationService.stopPositionStream();
    _isTrackingGps = false;
    _gpsStatusMessage = "GPS tracking stopped";
    notifyListeners();
  }
}

