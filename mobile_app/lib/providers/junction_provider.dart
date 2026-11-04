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

  List<JunctionModel> get nearbyJunctions => _nearbyJunctions;
  JunctionModel? get selectedJunction => _selectedJunction;
  Position? get currentPosition => _currentPosition;
  bool get isLoading => _isLoading;

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
}

