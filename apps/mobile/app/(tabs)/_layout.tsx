import { Tabs } from "expo-router";
import { useTranslation } from "react-i18next";

export default function TabsLayout() {
  const { t } = useTranslation();

  return (
    <Tabs
      screenOptions={{
        tabBarStyle: { backgroundColor: "#0b1120", borderTopColor: "#1e293b" },
        tabBarActiveTintColor: "#3b82f6",
        tabBarInactiveTintColor: "#64748b",
        headerStyle: { backgroundColor: "#0b1120" },
        headerTintColor: "#e2e8f0",
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: t("tabs.map"),
          tabBarLabel: t("tabs.map"),
        }}
      />
      <Tabs.Screen
        name="report"
        options={{
          title: t("tabs.report"),
          tabBarLabel: t("tabs.report"),
        }}
      />
      <Tabs.Screen
        name="route"
        options={{
          title: t("tabs.route"),
          tabBarLabel: t("tabs.route"),
        }}
      />
      <Tabs.Screen
        name="settings"
        options={{
          title: t("tabs.settings"),
          tabBarLabel: t("tabs.settings"),
        }}
      />
    </Tabs>
  );
}
