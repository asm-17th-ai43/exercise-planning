import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../env.dart';
import 'chat_chunk.dart';

/// SSE client for `POST /agent/chat`.
///
/// Flutter Web's `EventSource` only supports GET; the agent endpoint is POST,
/// so we drive the stream manually via `http.Client.send` and parse
/// `data: <json>\n\n` frames as they arrive.
class ChatClient {
  ChatClient({http.Client? httpClient, String? baseUrl})
      : _http = httpClient ?? http.Client(),
        _baseUrl = baseUrl ?? Env.backendBaseUrl;

  final http.Client _http;
  final String _baseUrl;

  /// Open a stream and yield [ChatChunk] as the server emits them.
  ///
  /// Throws on transport failure (non-2xx, network). Logical errors from the
  /// agent arrive as `ChatChunkType.error` chunks instead.
  Stream<ChatChunk> stream({
    required String message,
    String? threadId,
  }) async* {
    final uri = Uri.parse('$_baseUrl/agent/chat');
    final request = http.Request('POST', uri)
      ..headers['Content-Type'] = 'application/json'
      ..headers['Accept'] = 'text/event-stream'
      ..body = jsonEncode({
        'message': message,
        if (threadId != null) 'thread_id': threadId,
      });

    final response = await _http.send(request);
    if (response.statusCode != 200) {
      final body = await response.stream.bytesToString();
      throw ChatTransportException(
        'agent/chat ${response.statusCode}: $body',
      );
    }

    // sse-starlette emits `data: <json>\n\n`. Comments (`: ping`) and unknown
    // headers are ignored. Frames are delimited by a blank line.
    final lines = response.stream
        .transform(utf8.decoder)
        .transform(const LineSplitter());

    final dataBuffer = StringBuffer();
    await for (final line in lines) {
      if (line.isEmpty) {
        final raw = dataBuffer.toString();
        dataBuffer.clear();
        if (raw.isEmpty) continue;
        final decoded = jsonDecode(raw);
        if (decoded is Map<String, dynamic>) {
          yield ChatChunk.fromJson(decoded);
        }
      } else if (line.startsWith('data:')) {
        final value = line.substring(5);
        dataBuffer.write(value.startsWith(' ') ? value.substring(1) : value);
      }
      // Ignore `event:`, `id:`, `:`-prefixed comments.
    }

    // Flush any trailing frame that wasn't terminated by a blank line.
    final tail = dataBuffer.toString();
    if (tail.isNotEmpty) {
      final decoded = jsonDecode(tail);
      if (decoded is Map<String, dynamic>) {
        yield ChatChunk.fromJson(decoded);
      }
    }
  }

  void dispose() => _http.close();
}

class ChatTransportException implements Exception {
  ChatTransportException(this.message);
  final String message;
  @override
  String toString() => 'ChatTransportException: $message';
}
