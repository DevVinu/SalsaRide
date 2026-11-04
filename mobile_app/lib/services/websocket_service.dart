import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../config/app_config.dart';

class WebSocketService {
  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  bool _isConnected = false;

  bool get isConnected => _isConnected;

  void connect(String junctionId, Function(Map<String, dynamic>) onMessage) {
    disconnect();
    final url = '${AppConfig.wsBaseUrl}/junctions/$junctionId';
    try {
      _channel = WebSocketChannel.connect(Uri.parse(url));
      _isConnected = true;

      _subscription = _channel?.stream.listen(
        (message) {
          try {
            final data = jsonDecode(message);
            onMessage(data);
          } catch (e) {
            // parse error
          }
        },
        onError: (err) {
          _isConnected = false;
        },
        onDone: () {
          _isConnected = false;
        },
      );
    } catch (e) {
      _isConnected = false;
    }
  }

  void disconnect() {
    _subscription?.cancel();
    _channel?.sink.close();
    _channel = null;
    _isConnected = false;
  }
}

