import { getApps, initializeApp, type FirebaseOptions } from "@firebase/app";
import { getMessaging, getToken, isSupported } from "@firebase/messaging";
import api from "./api";

const firebaseConfig: FirebaseOptions = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

const hasFirebaseConfig = Object.values(firebaseConfig).every(Boolean);

export const canUsePushNotifications = () =>
  hasFirebaseConfig &&
  Boolean(import.meta.env.VITE_FIREBASE_VAPID_KEY) &&
  "Notification" in window &&
  "serviceWorker" in navigator;

const buildServiceWorkerUrl = () => {
  const params = new URLSearchParams({
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "",
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "",
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "",
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "",
    appId: import.meta.env.VITE_FIREBASE_APP_ID || "",
  });
  return `/firebase-messaging-sw.js?${params.toString()}`;
};

export const registerPushNotifications = async () => {
  if (!canUsePushNotifications() || !(await isSupported())) {
    return null;
  }

  const permission = await Notification.requestPermission();
  if (permission !== "granted") {
    return null;
  }

  const app = getApps()[0] ?? initializeApp(firebaseConfig);
  const messaging = getMessaging(app);
  const registration = await navigator.serviceWorker.register(buildServiceWorkerUrl());
  const token = await getToken(messaging, {
    vapidKey: import.meta.env.VITE_FIREBASE_VAPID_KEY,
    serviceWorkerRegistration: registration,
  });

  if (!token) {
    return null;
  }

  await api.post("/settings/notifications/devices/", {
    token,
    platform: "web",
  });
  return token;
};
