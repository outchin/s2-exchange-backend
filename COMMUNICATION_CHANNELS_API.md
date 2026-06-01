# Communication Channels API Documentation

## Overview

User က "ငွေလဲလှယ်မည်" button ကို နှိပ်လိုက်ရင် communication channels (Facebook, Telegram, Viber, etc.) list ကို ပြပေးဖို့ API။

---

## API Endpoint

```
GET /api/channels/
```

**Production URL:**
```
https://s2-exchange-backend-production.up.railway.app/api/channels/
```

**Authentication:** Not required (public endpoint)

---

## Request

**Method:** `GET`

**Headers:** None required

**Example:**
```dart
// Flutter/Dart
final response = await http.get(
  Uri.parse('https://s2-exchange-backend-production.up.railway.app/api/channels/'),
);
```

---

## Response

**Status Code:** `200 OK`

**Content-Type:** `application/json`

**Response Format:**
```json
[
  {
    "id": 1,
    "name": "Facebook Group",
    "platform": "facebook",
    "platform_display": "Facebook",
    "url": "https://www.facebook.com/groups/s2exchange",
    "icon_url": "https://cdn.simpleicons.org/facebook/1877F2",
    "description": "Join our Facebook group for exchange updates",
    "sort_order": 1
  },
  {
    "id": 2,
    "name": "Facebook Messenger",
    "platform": "messenger",
    "platform_display": "Facebook Messenger",
    "url": "https://m.me/s2exchange",
    "icon_url": "https://cdn.simpleicons.org/messenger/00B2FF",
    "description": "Chat with us on Messenger",
    "sort_order": 2
  },
  {
    "id": 3,
    "name": "Telegram",
    "platform": "telegram",
    "platform_display": "Telegram",
    "url": "https://t.me/s2exchange",
    "icon_url": "https://cdn.simpleicons.org/telegram/26A5E4",
    "description": "Contact us on Telegram",
    "sort_order": 3
  },
  {
    "id": 4,
    "name": "Viber",
    "platform": "viber",
    "platform_display": "Viber",
    "url": "viber://chat?number=%2B959123456789",
    "icon_url": "https://cdn.simpleicons.org/viber/7360F2",
    "description": "Call us on Viber",
    "sort_order": 4
  }
]
```

---

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique channel ID |
| `name` | string | Display name (e.g., "Facebook Group", "Telegram Support") |
| `platform` | string | Platform type: `facebook`, `messenger`, `telegram`, `viber`, `whatsapp`, `line`, `wechat`, `other` |
| `platform_display` | string | Human-readable platform name (e.g., "Facebook", "Telegram") |
| `url` | string | Redirect URL (Facebook group link, Telegram bot, Viber call, etc.) |
| `icon_url` | string | Icon/logo URL (default platform icons provided) |
| `description` | string | Short description text |
| `sort_order` | integer | Display order (lower numbers first) |

---

## Platform Types

Available platform values:

| Platform Code | Display Name | Example URL |
|---------------|--------------|-------------|
| `facebook` | Facebook | `https://www.facebook.com/groups/...` |
| `messenger` | Facebook Messenger | `https://m.me/...` or `fb-messenger://user-thread/...` |
| `telegram` | Telegram | `https://t.me/...` |
| `viber` | Viber | `viber://chat?number=...` |
| `whatsapp` | WhatsApp | `https://wa.me/...` |
| `line` | LINE | `https://line.me/R/ti/p/...` |
| `wechat` | WeChat | `weixin://...` |
| `other` | Other | Any custom URL |

---

## Flutter Implementation Example

### 1. Model Class

```dart
class CommunicationChannel {
  final int id;
  final String name;
  final String platform;
  final String platformDisplay;
  final String url;
  final String iconUrl;
  final String description;
  final int sortOrder;

  CommunicationChannel({
    required this.id,
    required this.name,
    required this.platform,
    required this.platformDisplay,
    required this.url,
    required this.iconUrl,
    required this.description,
    required this.sortOrder,
  });

  factory CommunicationChannel.fromJson(Map<String, dynamic> json) {
    return CommunicationChannel(
      id: json['id'],
      name: json['name'],
      platform: json['platform'],
      platformDisplay: json['platform_display'],
      url: json['url'],
      iconUrl: json['icon_url'],
      description: json['description'],
      sortOrder: json['sort_order'],
    );
  }
}
```

### 2. API Service

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ChannelService {
  static const String baseUrl = 'https://s2-exchange-backend-production.up.railway.app/api';

  Future<List<CommunicationChannel>> getChannels() async {
    final response = await http.get(
      Uri.parse('$baseUrl/channels/'),
    );

    if (response.statusCode == 200) {
      List<dynamic> data = json.decode(response.body);
      return data.map((json) => CommunicationChannel.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load channels');
    }
  }
}
```

### 3. UI Implementation

```dart
class ExchangeConfirmationScreen extends StatefulWidget {
  @override
  _ExchangeConfirmationScreenState createState() => _ExchangeConfirmationScreenState();
}

class _ExchangeConfirmationScreenState extends State<ExchangeConfirmationScreen> {
  List<CommunicationChannel> channels = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    loadChannels();
  }

  Future<void> loadChannels() async {
    try {
      final channelService = ChannelService();
      final loadedChannels = await channelService.getChannels();
      setState(() {
        channels = loadedChannels;
        isLoading = false;
      });
    } catch (e) {
      print('Error loading channels: $e');
      setState(() {
        isLoading = false;
      });
    }
  }

  void openChannel(CommunicationChannel channel) async {
    final uri = Uri.parse(channel.url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Cannot open ${channel.name}')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('ငွေလဲလှယ်မည်')),
      body: isLoading
        ? Center(child: CircularProgressIndicator())
        : ListView.builder(
            itemCount: channels.length,
            itemBuilder: (context, index) {
              final channel = channels[index];
              return ListTile(
                leading: Image.network(
                  channel.iconUrl,
                  width: 40,
                  height: 40,
                  errorBuilder: (context, error, stackTrace) {
                    return Icon(Icons.chat, size: 40);
                  },
                ),
                title: Text(channel.name),
                subtitle: Text(channel.description),
                trailing: Icon(Icons.arrow_forward_ios),
                onTap: () => openChannel(channel),
              );
            },
          ),
    );
  }
}
```

### 4. URL Launcher Setup

Add to `pubspec.yaml`:
```yaml
dependencies:
  url_launcher: ^6.1.0
```

Android `AndroidManifest.xml`:
```xml
<queries>
  <intent>
    <action android:name="android.intent.action.VIEW" />
    <data android:scheme="https" />
  </intent>
  <intent>
    <action android:name="android.intent.action.VIEW" />
    <data android:scheme="viber" />
  </intent>
  <intent>
    <action android:name="android.intent.action.VIEW" />
    <data android:scheme="fb-messenger" />
  </intent>
  <intent>
    <action android:name="android.intent.action.VIEW" />
    <data android:scheme="whatsapp" />
  </intent>
</queries>
```

---

## User Flow

```
1. User converts currency amount
   ↓
2. User taps "ငွေလဲလှယ်မည်" button
   ↓
3. App calls GET /api/channels/
   ↓
4. Display bottom sheet/modal with channel options
   ↓
5. User selects a channel (Facebook/Telegram/Viber)
   ↓
6. App opens channel.url (redirect to Facebook group, Telegram bot, Viber call)
   ↓
7. User contacts support via selected channel
```

---

## Admin Panel Management

Admin can add/edit/remove channels at:
```
https://s2-exchange-backend-production.up.railway.app/admin/exchange/communicationchannel/
```

**Fields:**
- **Name:** Display name (e.g., "Facebook Group")
- **Platform:** Select from dropdown (Facebook, Telegram, Viber, etc.)
- **URL:** Redirect URL (e.g., `https://www.facebook.com/groups/...`)
- **Icon URL:** Optional custom icon (defaults to platform icon)
- **Description:** Short text (e.g., "Chat with us on Messenger")
- **Is Active:** Show/hide channel
- **Sort Order:** Display order (0 = first)

---

## Default Platform Icons

If admin doesn't provide custom icon, default icons are used from Simple Icons CDN:

| Platform | Icon URL (Simple Icons CDN) |
|----------|---------------------|
| Facebook | `https://cdn.simpleicons.org/facebook/1877F2` |
| Messenger | `https://cdn.simpleicons.org/messenger/00B2FF` |
| Telegram | `https://cdn.simpleicons.org/telegram/26A5E4` |
| Viber | `https://cdn.simpleicons.org/viber/7360F2` |
| WhatsApp | `https://cdn.simpleicons.org/whatsapp/25D366` |
| LINE | `https://cdn.simpleicons.org/line/00C300` |
| WeChat | `https://cdn.simpleicons.org/wechat/07C160` |

---

## Error Handling

### Empty Response
```json
[]
```
If no channels are configured, empty array is returned.

### Network Error
```dart
try {
  final channels = await channelService.getChannels();
} catch (e) {
  // Handle error - show retry button or use fallback channels
  print('Error: $e');
}
```

---

## Testing

### Test API Endpoint

**cURL:**
```bash
curl https://s2-exchange-backend-production.up.railway.app/api/channels/
```

**Postman:**
```
GET https://s2-exchange-backend-production.up.railway.app/api/channels/
```

**Expected Response:** JSON array of channel objects

---

## Notes

1. **Dynamic:** Admin can add/remove/edit channels without app update
2. **Flexible:** Support any platform (Facebook, Telegram, Viber, WhatsApp, custom URLs)
3. **Icons:** Default platform icons provided (SVG format from Simple Icons CDN)
4. **Ordering:** Channels sorted by `sort_order` field (admin controlled)
5. **Active/Inactive:** Admin can temporarily hide channels without deleting

---

## Summary for Mobile Team

**ဘာလုပ်ရမလဲ:**

1. **API ခေါ်မယ်:** `GET /api/channels/`
2. **Response ရမယ်:** Channel list with name, platform, url, icon_url, description
3. **UI ပြမယ်:** Bottom sheet or modal with channel list
4. **User select လုပ်မယ်:** User taps a channel
5. **Redirect လုပ်မယ်:** `launchUrl(channel.url)` - opens Facebook/Telegram/Viber app

**Admin က control လုပ်တာ:**
- Which channels to show (Facebook, Telegram, Viber, etc.)
- URLs for each channel
- Order and display names
- Enable/disable channels

**Mobile team က လုပ်စရာမရှိတာ:**
- URL တွေ hardcode မလုပ်ရ
- Platform list hardcode မလုပ်ရ
- အားလုံး API ကနေ dynamic ရလာမယ်!
