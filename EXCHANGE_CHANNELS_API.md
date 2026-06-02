# Exchange Communication Channels API Documentation

## Overview

ငွေလဲလှယ်ရန် (Exchange) အတွက် သီးခြား communication channels API။ Follow Us channels (groups) နဲ့ မတူပါဘူး - ဒါက direct messaging/chat channels တွေအတွက်ပါ။

**ခြားနားချက်:**
- **Follow Us Channels** (`/api/channels/`): Community groups, updates channels (Facebook Groups, Telegram Channels, etc.)
- **Exchange Channels** (`/api/exchange-channels/`): Direct messaging for exchange transactions (Facebook Messenger, Telegram Bot, etc.)

---

## API Endpoint

```
GET /api/exchange-channels/
```

**Production URL:**
```
https://s2-exchange-backend-production.up.railway.app/api/exchange-channels/
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
  Uri.parse('https://s2-exchange-backend-production.up.railway.app/api/exchange-channels/'),
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
    "name": "Email",
    "platform": "email",
    "platform_display": "Email",
    "url": "mailto:contact@s2exchange.com",
    "icon_url": "https://cdn.simpleicons.org/gmail/EA4335",
    "description": "Send us an email",
    "is_primary": true,
    "sort_order": 1
  },
  {
    "id": 2,
    "name": "Phone",
    "platform": "phone",
    "platform_display": "Phone",
    "url": "tel:+959123456789",
    "icon_url": "https://cdn.simpleicons.org/phone/34A853",
    "description": "Call us directly",
    "is_primary": true,
    "sort_order": 2
  },
  {
    "id": 3,
    "name": "Website",
    "platform": "website",
    "platform_display": "Website",
    "url": "https://s2exchange.com",
    "icon_url": "https://cdn.simpleicons.org/googlechrome/4285F4",
    "description": "Visit our website",
    "is_primary": true,
    "sort_order": 3
  },
  {
    "id": 4,
    "name": "Facebook Messenger",
    "platform": "messenger",
    "platform_display": "Facebook Messenger",
    "url": "https://m.me/s2exchange",
    "icon_url": "https://cdn.simpleicons.org/messenger/00B2FF",
    "description": "Chat with us on Messenger",
    "is_primary": false,
    "sort_order": 4
  },
  {
    "id": 5,
    "name": "Telegram",
    "platform": "telegram",
    "platform_display": "Telegram",
    "url": "https://t.me/s2exchange_bot",
    "icon_url": "https://cdn.simpleicons.org/telegram/26A5E4",
    "description": "Contact us on Telegram",
    "is_primary": false,
    "sort_order": 5
  },
  {
    "id": 6,
    "name": "Facebook Page",
    "platform": "facebook",
    "platform_display": "Facebook",
    "url": "https://www.facebook.com/s2exchange",
    "icon_url": "https://cdn.simpleicons.org/facebook/1877F2",
    "description": "Message us on Facebook",
    "is_primary": false,
    "sort_order": 6
  }
]
```

---

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique channel ID |
| `name` | string | Display name (e.g., "Email", "Phone", "Facebook Messenger") |
| `platform` | string | Platform type: `email`, `phone`, `website`, `facebook`, `messenger`, `telegram`, `viber`, `whatsapp`, `line`, `wechat`, `other` |
| `platform_display` | string | Human-readable platform name (e.g., "Email", "Phone", "Facebook Messenger") |
| `url` | string | Contact URL (mailto:, tel:, https://, m.me, etc.) |
| `icon_url` | string | Icon/logo URL (default platform icons provided) |
| `description` | string | Short description text |
| `is_primary` | boolean | **true** for primary contact (email, phone, website), **false** for additional channels |
| `sort_order` | integer | Display order (lower numbers first) |

---

## Platform Types

Available platform values:

| Platform Code | Display Name | Example URL | Type |
|---------------|--------------|-------------|------|
| `email` | Email | `mailto:contact@example.com` | Primary |
| `phone` | Phone | `tel:+959123456789` | Primary |
| `website` | Website | `https://example.com` | Primary |
| `facebook` | Facebook | `https://www.facebook.com/...` | Additional |
| `messenger` | Facebook Messenger | `https://m.me/...` | Additional |
| `telegram` | Telegram | `https://t.me/...` | Additional |
| `viber` | Viber | `viber://chat?number=...` | Additional |
| `whatsapp` | WhatsApp | `https://wa.me/...` | Additional |
| `line` | LINE | `https://line.me/R/ti/p/...` | Additional |
| `wechat` | WeChat | `weixin://...` | Additional |
| `other` | Other | Any custom URL | Additional |

---

## Flutter Implementation Example

### 1. Model Class

```dart
class ExchangeCommunicationChannel {
  final int id;
  final String name;
  final String platform;
  final String platformDisplay;
  final String url;
  final String iconUrl;
  final String description;
  final bool isPrimary;
  final int sortOrder;

  ExchangeCommunicationChannel({
    required this.id,
    required this.name,
    required this.platform,
    required this.platformDisplay,
    required this.url,
    required this.iconUrl,
    required this.description,
    required this.isPrimary,
    required this.sortOrder,
  });

  factory ExchangeCommunicationChannel.fromJson(Map<String, dynamic> json) {
    return ExchangeCommunicationChannel(
      id: json['id'],
      name: json['name'],
      platform: json['platform'],
      platformDisplay: json['platform_display'],
      url: json['url'],
      iconUrl: json['icon_url'],
      description: json['description'],
      isPrimary: json['is_primary'],
      sortOrder: json['sort_order'],
    );
  }
}
```

### 2. API Service

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ExchangeChannelService {
  static const String baseUrl = 'https://s2-exchange-backend-production.up.railway.app/api';

  Future<List<ExchangeCommunicationChannel>> getExchangeChannels() async {
    final response = await http.get(
      Uri.parse('$baseUrl/exchange-channels/'),
    );

    if (response.statusCode == 200) {
      List<dynamic> data = json.decode(response.body);
      return data.map((json) => ExchangeCommunicationChannel.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load exchange channels');
    }
  }
}
```

### 3. UI Implementation

```dart
class ExchangeContactScreen extends StatefulWidget {
  @override
  _ExchangeContactScreenState createState() => _ExchangeContactScreenState();
}

class _ExchangeContactScreenState extends State<ExchangeContactScreen> {
  List<ExchangeCommunicationChannel> channels = [];
  bool isLoading = true;

  // Separate primary and additional channels
  List<ExchangeCommunicationChannel> get primaryChannels =>
      channels.where((c) => c.isPrimary).toList();

  List<ExchangeCommunicationChannel> get additionalChannels =>
      channels.where((c) => !c.isPrimary).toList();

  @override
  void initState() {
    super.initState();
    loadChannels();
  }

  Future<void> loadChannels() async {
    try {
      final channelService = ExchangeChannelService();
      final loadedChannels = await channelService.getExchangeChannels();
      setState(() {
        channels = loadedChannels;
        isLoading = false;
      });
    } catch (e) {
      print('Error loading exchange channels: $e');
      setState(() {
        isLoading = false;
      });
    }
  }

  void openChannel(ExchangeCommunicationChannel channel) async {
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
      appBar: AppBar(title: Text('ဆက်သွယ်ရန်')),
      body: isLoading
        ? Center(child: CircularProgressIndicator())
        : SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Primary Contact Section
                if (primaryChannels.isNotEmpty) ...[
                  Padding(
                    padding: EdgeInsets.fromLTRB(16, 16, 16, 8),
                    child: Text(
                      'Primary Contact',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  ...primaryChannels.map((channel) => Card(
                    margin: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                    child: ListTile(
                      leading: Image.network(
                        channel.iconUrl,
                        width: 40,
                        height: 40,
                        errorBuilder: (context, error, stackTrace) {
                          return Icon(Icons.contact_mail, size: 40);
                        },
                      ),
                      title: Text(channel.name),
                      subtitle: Text(channel.description),
                      trailing: Icon(Icons.arrow_forward_ios),
                      onTap: () => openChannel(channel),
                    ),
                  )).toList(),
                ],

                // Additional Channels Section
                if (additionalChannels.isNotEmpty) ...[
                  Padding(
                    padding: EdgeInsets.fromLTRB(16, 24, 16, 8),
                    child: Text(
                      'Additional Channels',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  ...additionalChannels.map((channel) => Card(
                    margin: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                    child: ListTile(
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
                    ),
                  )).toList(),
                ],

                SizedBox(height: 16),
              ],
            ),
          ),
    );
  }
}
```

---

## User Flow

```
1. User calculates exchange amount
   ↓
2. User taps "ငွေလဲလှယ်မည်" button
   ↓
3. App calls GET /api/exchange-channels/
   ↓
4. Display bottom sheet/modal with exchange channel options
   ↓
5. User selects a channel (Facebook Messenger/Telegram/etc.)
   ↓
6. App opens channel.url (direct message link)
   ↓
7. User contacts support via selected channel to complete exchange
```

---

## Admin Panel Management

Admin can add/edit/remove exchange channels at:
```
https://s2-exchange-backend-production.up.railway.app/admin/exchange/exchangecommunicationchannel/
```

**Fields:**
- **Name:** Display name (e.g., "Facebook Messenger")
- **Platform:** Select from dropdown (Messenger, Telegram, etc.)
- **URL:** Direct messaging URL (e.g., `https://m.me/...`)
- **Icon URL:** Optional custom icon (defaults to platform icon)
- **Description:** Short text (e.g., "Chat with us on Messenger for exchange")
- **Is Active:** Show/hide channel
- **Sort Order:** Display order (0 = first)

---

## Default Platform Icons

If admin doesn't provide custom icon, default icons are used from Simple Icons CDN:

| Platform | Icon URL (Simple Icons CDN) |
|----------|---------------------|
| Email | `https://cdn.simpleicons.org/gmail/EA4335` |
| Phone | `https://cdn.simpleicons.org/phone/34A853` |
| Website | `https://cdn.simpleicons.org/googlechrome/4285F4` |
| Facebook | `https://cdn.simpleicons.org/facebook/1877F2` |
| Messenger | `https://cdn.simpleicons.org/messenger/00B2FF` |
| Telegram | `https://cdn.simpleicons.org/telegram/26A5E4` |
| Viber | `https://cdn.simpleicons.org/viber/7360F2` |
| WhatsApp | `https://cdn.simpleicons.org/whatsapp/25D366` |
| LINE | `https://cdn.simpleicons.org/line/00C300` |
| WeChat | `https://cdn.simpleicons.org/wechat/07C160` |

---

## Testing

### Test API Endpoint

**cURL:**
```bash
curl https://s2-exchange-backend-production.up.railway.app/api/exchange-channels/
```

**Postman:**
```
GET https://s2-exchange-backend-production.up.railway.app/api/exchange-channels/
```

**Expected Response:** JSON array of exchange channel objects

---

## Seeding Mock Data

To populate initial exchange channels:

```bash
python manage.py seed_exchange_channels
```

This will create:
- **Primary Channels:** Email, Phone, Website
- **Additional Channels:** Facebook Messenger, Telegram, Facebook Page

---

## Summary

**အဓိက ခြားနားချက်များ:**

| Feature | Follow Us Channels | Exchange Channels |
|---------|-------------------|-------------------|
| **Endpoint** | `/api/channels/` | `/api/exchange-channels/` |
| **Purpose** | Community groups, updates | Direct messaging for exchange |
| **Example URLs** | Facebook Groups, Telegram Channels | Facebook Messenger, Telegram Bot |
| **Use Case** | Follow for updates | Contact for exchange transactions |
| **Admin Panel** | `CommunicationChannel` | `ExchangeCommunicationChannel` |

**Mobile Team:**
1. **Follow Us** အတွက် `/api/channels/` သုံးမယ်
2. **ငွေလဲလှယ်ရန်** အတွက် `/api/exchange-channels/` သုံးမယ်
3. နှစ်ခု သီးခြား API ဖြစ်တယ်
4. Admin က နှစ်ခု သီးခြား manage လုပ်နိုင်တယ်

## UI Layout Recommendation

**ဆက်သွယ်ရန် Page မှာ ခွဲပြီး ပြပေးမယ်:**

```
┌─────────────────────────────┐
│      ဆက်သွယ်ရန်            │
├─────────────────────────────┤
│                             │
│ Primary Contact             │
│ ┌─────────────────────────┐ │
│ │ 📧 Email                 │ │
│ │ Send us an email        │ │
│ └─────────────────────────┘ │
│ ┌─────────────────────────┐ │
│ │ 📞 Phone                 │ │
│ │ Call us directly        │ │
│ └─────────────────────────┘ │
│ ┌─────────────────────────┐ │
│ │ 🌐 Website               │ │
│ │ Visit our website       │ │
│ └─────────────────────────┘ │
│                             │
│ Additional Channels         │
│ ┌─────────────────────────┐ │
│ │ 💬 Facebook Messenger    │ │
│ │ Chat with us on Messenger│ │
│ └─────────────────────────┘ │
│ ┌─────────────────────────┐ │
│ │ ✈️ Telegram              │ │
│ │ Contact us on Telegram  │ │
│ └─────────────────────────┘ │
│ ┌─────────────────────────┐ │
│ │ 👥 Facebook Page         │ │
│ │ Message us on Facebook  │ │
│ └─────────────────────────┘ │
└─────────────────────────────┘
```

**Key Points:**
- `is_primary: true` ဆိုရင် **Primary Contact** section မှာ ပြမယ်
- `is_primary: false` ဆိုရင် **Additional Channels** section မှာ ပြမယ်
- Email က `mailto:` link ဖွင့်မယ်
- Phone က `tel:` dialer ဖွင့်မယ်
- Website က browser ဖွင့်မယ်
- Messenger/Telegram/Facebook က respective app ဖွင့်မယ်
- အကုန်လုံး backend ကနေ dynamic ရလာတယ်
