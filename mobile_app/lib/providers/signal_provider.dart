import 'package:flutter/material.dart';
import '../models/signal_model.dart';
import '../services/api_service.dart';
import '../services/websocket_service.dart';

class SignalProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();
  final WebSocketService _wsService = WebSocketService();

  VirtualSignalModel? _signalState;
  UserSignalAdvisoryModel? _advisory;
  String? _activeJunctionId;

  VirtualSignalModel? get signalState => _signalState;
  UserSignalAdvisoryModel? get advisory => _advisory;
  bool get isConnected => _wsService.isConnected;

  void subscribeToJunction(String junctionId) {
    if (_activeJunctionId == junctionId && _wsService.isConnected) return;

    _activeJunctionId = junctionId;
    _fetchInitialState(junctionId);

    _wsService.connect(junctionId, (data) {
      if (data['signal_state'] != null) {
        _signalState = VirtualSignalModel.fromJson(data['signal_state']);
        notifyListeners();
      }
    });
  }

  Future<void> _fetchInitialState(String junctionId) async {
    try {
      _signalState = await _apiService.getSignalState(junctionId);
      notifyListeners();
    } catch (e) {
      // initial fetch error
    }
  }

  void updateAdvisory(UserSignalAdvisoryModel advisory) {
    _advisory = advisory;
    notifyListeners();
  }

  @override
  void dispose() {
    _wsService.disconnect();
    super.dispose();
  }
}

