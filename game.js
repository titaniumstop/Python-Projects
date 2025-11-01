// Game Constants
const SCREEN_WIDTH = 1024;
const SCREEN_HEIGHT = 768;
const FPS = 60;
const TILE_SIZE = 64;

// Colors
const WHITE = '#FFFFFF';
const BLACK = '#000000';
const RED = '#FF0000';
const GREEN = '#00FF00';
const BLUE = '#0000FF';
const GRAY = '#808080';
const DARK_GRAY = '#404040';
const YELLOW = '#FFFF00';

// Game state
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
canvas.width = SCREEN_WIDTH;
canvas.height = SCREEN_HEIGHT;

// Player class
class Player {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.angle = 0;
        this.health = 100;
        this.ammo = 30;
        this.speed = 3;
        this.width = 20;
        this.height = 20;
    }
    
    move(keys, mapData) {
        const oldX = this.x;
        const oldY = this.y;
        
        if (keys['w'] || keys['ArrowUp']) {
            this.x += Math.cos(this.angle) * this.speed;
            this.y += Math.sin(this.angle) * this.speed;
        }
        if (keys['s'] || keys['ArrowDown']) {
            this.x -= Math.cos(this.angle) * this.speed;
            this.y -= Math.sin(this.angle) * this.speed;
        }
        if (keys['a'] || keys['ArrowLeft']) {
            this.x += Math.cos(this.angle - Math.PI/2) * this.speed;
            this.y += Math.sin(this.angle - Math.PI/2) * this.speed;
        }
        if (keys['d'] || keys['ArrowRight']) {
            this.x += Math.cos(this.angle + Math.PI/2) * this.speed;
            this.y += Math.sin(this.angle + Math.PI/2) * this.speed;
        }
        
        // Check wall collision
        const gridX = Math.floor(this.x / TILE_SIZE);
        const gridY = Math.floor(this.y / TILE_SIZE);
        if (gridX >= 0 && gridX < mapData[0].length && gridY >= 0 && gridY < mapData.length) {
            if (mapData[gridY][gridX] === 1) {
                this.x = oldX;
                this.y = oldY;
            } else {
                this.x = Math.max(this.width, Math.min(SCREEN_WIDTH - this.width, this.x));
                this.y = Math.max(this.height, Math.min(SCREEN_HEIGHT - this.height, this.y));
            }
        }
    }
    
    rotate(mouseMovement) {
        const sensitivity = 0.003;
        this.angle += mouseMovement * sensitivity;
    }
    
    shoot() {
        if (this.ammo > 0) {
            this.ammo -= 1;
            return true;
        }
        return false;
    }
}

// Enemy class
class Enemy {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.angle = 0;
        this.health = 50;
        this.speed = 2.0;
        this.width = 20;
        this.height = 20;
        this.cooldown = 60;
        this.cooldownTimer = 0;
        this.dist = 0;
    }
    
    update(player) {
        const dx = player.x - this.x;
        const dy = player.y - this.y;
        this.dist = dx*dx + dy*dy > 0 ? Math.sqrt(dx*dx + dy*dy) : 1;
        
        if (this.dist > 0) {
            this.x += (dx / this.dist) * this.speed;
            this.y += (dy / this.dist) * this.speed;
            this.angle = Math.atan2(dy, dx);
        }
        
        if (this.cooldownTimer > 0) {
            this.cooldownTimer -= 1;
        }
    }
    
    canShoot() {
        return this.cooldownTimer === 0;
    }
    
    shoot() {
        if (this.canShoot()) {
            this.cooldownTimer = this.cooldown;
            return true;
        }
        return false;
    }
}

// Bullet class
class Bullet {
    constructor(x, y, angle, owner) {
        this.x = x;
        this.y = y;
        this.angle = angle;
        this.speed = 15;
        this.owner = owner;
        this.damage = owner === 'player' ? 25 : 10;
    }
    
    update() {
        this.x += Math.cos(this.angle) * this.speed;
        this.y += Math.sin(this.angle) * this.speed;
    }
    
    isOffScreen() {
        return this.x < 0 || this.x > SCREEN_WIDTH || this.y < 0 || this.y > SCREEN_HEIGHT;
    }
}

// Game class
class FPSGame {
    constructor() {
        this.running = true;
        this.mapData = this.createMap();
        this.player = new Player(200, 200);
        this.enemies = [
            new Enemy(600, 300),
            new Enemy(700, 500),
            new Enemy(800, 200)
        ];
        this.bullets = [];
        this.score = 0;
        this.keys = {};
        this.mouseX = 0;
        this.mouseY = 0;
        this.lastMouseX = SCREEN_WIDTH / 2;
        this.lastShotTime = 0;
        this.maxEnemies = 10;
        this.enemySpawnTimer = 0;
        this.enemySpawnDelay = 120;
        this.lastTime = performance.now();
        
        this.setupEventListeners();
        this.gameLoop();
    }
    
    createMap() {
        const mapData = Array(12).fill(0).map(() => Array(16).fill(0));
        
        // Border walls
        for (let i = 0; i < 16; i++) {
            mapData[0][i] = 1;
            mapData[11][i] = 1;
        }
        for (let i = 0; i < 12; i++) {
            mapData[i][0] = 1;
            mapData[i][15] = 1;
        }
        
        // Internal walls
        for (let i = 5; i < 10; i++) {
            mapData[3][i] = 1;
            mapData[8][i] = 1;
        }
        for (let i = 4; i < 9; i++) {
            mapData[i][7] = 1;
            mapData[i][12] = 1;
        }
        
        return mapData;
    }
    
    setupEventListeners() {
        // Keyboard
        document.addEventListener('keydown', (e) => {
            const key = e.key.toLowerCase();
            this.keys[key] = true;
            if (key === 'r') {
                if (this.player.ammo < 30) {
                    this.player.ammo = 30;
                }
            }
        });
        
        document.addEventListener('keyup', (e) => {
            this.keys[e.key.toLowerCase()] = false;
        });
        
        // Mouse
        document.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            this.mouseX = e.clientX - rect.left;
            this.mouseY = e.clientY - rect.top;
        });
        
        canvas.addEventListener('click', (e) => {
            if (this.player.ammo > 0) {
                const currentTime = performance.now();
                if (currentTime - this.lastShotTime > 200) {
                    this.player.shoot();
                    this.bullets.push(new Bullet(this.player.x, this.player.y, this.player.angle, 'player'));
                    this.lastShotTime = currentTime;
                }
            }
        });
        
        // Lock pointer (workaround for browsers)
        canvas.addEventListener('click', () => {
            canvas.requestPointerLock = canvas.requestPointerLock || canvas.mozRequestPointerLock;
            canvas.requestPointerLock();
        });
        
        // Handle pointer lock change
        document.addEventListener('pointerlockchange', this.handlePointerLockChange.bind(this), false);
        document.addEventListener('mozpointerlockchange', this.handlePointerLockChange.bind(this), false);
    }
    
    handlePointerLockChange() {
        const isLocked = document.pointerLockElement === canvas || document.mozPointerLockElement === canvas;
        
        if (isLocked) {
            document.addEventListener('mousemove', this.handleMouseMove.bind(this), false);
        } else {
            document.removeEventListener('mousemove', this.handleMouseMove.bind(this), false);
        }
    }
    
    handleMouseMove(e) {
        const sensitivity = 0.003;
        this.player.angle += e.movementX * sensitivity;
    }
    
    drawMap() {
        for (let y = 0; y < this.mapData.length; y++) {
            for (let x = 0; x < this.mapData[y].length; x++) {
                const rect = {
                    x: x * TILE_SIZE,
                    y: y * TILE_SIZE,
                    width: TILE_SIZE,
                    height: TILE_SIZE
                };
                
                if (this.mapData[y][x] === 1) {
                    ctx.fillStyle = DARK_GRAY;
                    ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
                    ctx.strokeStyle = BLACK;
                    ctx.lineWidth = 2;
                    ctx.strokeRect(rect.x, rect.y, rect.width, rect.height);
                } else {
                    ctx.fillStyle = GRAY;
                    ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
                    ctx.strokeStyle = BLACK;
                    ctx.lineWidth = 1;
                    ctx.strokeRect(rect.x, rect.y, rect.width, rect.height);
                }
            }
        }
    }
    
    drawPlayer() {
        ctx.fillStyle = BLUE;
        ctx.beginPath();
        ctx.arc(this.player.x, this.player.y, this.player.width / 2, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.strokeStyle = BLUE;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(this.player.x, this.player.y);
        ctx.lineTo(
            this.player.x + Math.cos(this.player.angle) * 30,
            this.player.y + Math.sin(this.player.angle) * 30
        );
        ctx.stroke();
    }
    
    drawEnemies() {
        for (const enemy of this.enemies) {
            ctx.fillStyle = RED;
            ctx.beginPath();
            ctx.arc(enemy.x, enemy.y, enemy.width / 2, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.strokeStyle = RED;
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(enemy.x, enemy.y);
            ctx.lineTo(
                enemy.x + Math.cos(enemy.angle) * 30,
                enemy.y + Math.sin(enemy.angle) * 30
            );
            ctx.stroke();
        }
    }
    
    drawBullets() {
        for (const bullet of this.bullets) {
            ctx.fillStyle = bullet.owner === 'player' ? YELLOW : RED;
            ctx.beginPath();
            ctx.arc(bullet.x, bullet.y, 5, 0, Math.PI * 2);
            ctx.fill();
        }
    }
    
    updateHUD() {
        const healthBar = document.getElementById('healthBar');
        healthBar.style.setProperty('--health', this.player.health + '%');
        document.getElementById('healthText').textContent = `Health: ${this.player.health}`;
        document.getElementById('ammoDisplay').textContent = this.player.ammo;
        document.getElementById('scoreDisplay').textContent = this.score;
        document.getElementById('enemiesDisplay').textContent = this.enemies.length;
    }
    
    checkBulletCollisions() {
        for (let i = this.bullets.length - 1; i >= 0; i--) {
            const bullet = this.bullets[i];
            
            if (bullet.isOffScreen()) {
                this.bullets.splice(i, 1);
                continue;
            }
            
            // Wall collision
            const gridX = Math.floor(bullet.x / TILE_SIZE);
            const gridY = Math.floor(bullet.y / TILE_SIZE);
            if (gridX >= 0 && gridX < this.mapData[0].length && gridY >= 0 && gridY < this.mapData.length) {
                if (this.mapData[gridY][gridX] === 1) {
                    this.bullets.splice(i, 1);
                    continue;
                }
            }
            
            // Player collision
            if (bullet.owner === 'enemy') {
                const dx = bullet.x - this.player.x;
                const dy = bullet.y - this.player.y;
                const distSq = dx*dx + dy*dy;
                if (distSq < this.player.width * this.player.width) {
                    this.player.health -= bullet.damage;
                    this.bullets.splice(i, 1);
                    if (this.player.health <= 0) {
                        this.gameOver();
                    }
                    continue;
                }
            }
            
            // Enemy collision
            if (bullet.owner === 'player') {
                for (const enemy of this.enemies) {
                    const dx = bullet.x - enemy.x;
                    const dy = bullet.y - enemy.y;
                    const distSq = dx*dx + dy*dy;
                    if (distSq < enemy.width * enemy.width) {
                        enemy.health -= bullet.damage;
                        this.bullets.splice(i, 1);
                        if (enemy.health <= 0) {
                            this.score += 100;
                        }
                        break;
                    }
                }
            }
        }
    }
    
    updateEnemies() {
        this.enemies = this.enemies.filter(e => e.health > 0);
        
        for (const enemy of this.enemies) {
            enemy.update(this.player);
            
            if (enemy.canShoot()) {
                if (enemy.dist < 300 && Math.random() < 0.02) {
                    enemy.shoot();
                    this.bullets.push(new Bullet(enemy.x, enemy.y, enemy.angle, 'enemy'));
                }
            }
        }
    }
    
    spawnEnemy() {
        let attempts = 0;
        const maxAttempts = 50;
        
        while (attempts < maxAttempts) {
            const side = Math.floor(Math.random() * 4);
            let x, y;
            
            if (side === 0) {
                x = Math.random() * (SCREEN_WIDTH - 128) + 64;
                y = 64;
            } else if (side === 1) {
                x = Math.random() * (SCREEN_WIDTH - 128) + 64;
                y = SCREEN_HEIGHT - 64;
            } else if (side === 2) {
                x = 64;
                y = Math.random() * (SCREEN_HEIGHT - 128) + 64;
            } else {
                x = SCREEN_WIDTH - 64;
                y = Math.random() * (SCREEN_HEIGHT - 128) + 64;
            }
            
            const gridX = Math.floor(x / TILE_SIZE);
            const gridY = Math.floor(y / TILE_SIZE);
            const distToPlayer = Math.sqrt((x - this.player.x)**2 + (y - this.player.y)**2);
            
            if (gridX >= 0 && gridX < this.mapData[0].length && 
                gridY >= 0 && gridY < this.mapData.length &&
                this.mapData[gridY][gridX] === 0 && distToPlayer > 200) {
                this.enemies.push(new Enemy(x, y));
                return;
            }
            
            attempts++;
        }
        
        this.enemies.push(new Enemy(50, 50));
    }
    
    gameOver() {
        this.running = false;
        document.getElementById('finalScore').textContent = this.score;
        document.getElementById('gameOver').classList.remove('hidden');
    }
    
    gameLoop() {
        if (!this.running) return;
        
        const currentTime = performance.now();
        const deltaTime = currentTime - this.lastTime;
        this.lastTime = currentTime;
        
        // Player movement
        this.player.move(this.keys, this.mapData);
        
        // Update enemies
        this.updateEnemies();
        
        // Spawn enemies
        const aliveEnemies = this.enemies.length;
        if (aliveEnemies < this.maxEnemies) {
            this.enemySpawnTimer++;
            if (this.enemySpawnTimer >= this.enemySpawnDelay) {
                this.spawnEnemy();
                this.enemySpawnTimer = 0;
            }
        } else {
            this.enemySpawnTimer = 0;
        }
        
        // Update bullets
        for (const bullet of this.bullets) {
            bullet.update();
        }
        
        // Check collisions
        this.checkBulletCollisions();
        
        // Draw everything
        ctx.fillStyle = BLACK;
        ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);
        
        this.drawMap();
        this.drawEnemies();
        this.drawPlayer();
        this.drawBullets();
        this.updateHUD();
        
        requestAnimationFrame(() => this.gameLoop());
    }
}

// Start game when page loads
window.addEventListener('load', () => {
    new FPSGame();
});

