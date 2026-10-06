-- Процедурная карта-остров для Roblox.
-- Установка: вставьте как Script в ServerScriptService и нажмите Play.
-- Один и тот же Seed даёт одну и ту же карту. Seed = nil -> случайная карта каждый раз.

local Lighting = game:GetService("Lighting")

local CONFIG = {
	Seed = nil, -- например 12345, чтобы карта была одинаковой
	Size = 320, -- размер карты в студах (лучше кратно 8)
	Cell = 4, -- размер ячейки рельефа (равен вокселю Terrain)
	MaxHeight = 44, -- максимальная высота холмов
	WaterLevel = 6, -- уровень воды
	NoiseScale = 0.012, -- меньше -> более плавные и широкие холмы
	SpawnRadius = 24, -- радиус ровной площадки в центре
	SpawnHeight = 12, -- высота площадки спавна
	TreeCount = 160,
	RockCount = 70,
}

local rng = Random.new(CONFIG.Seed or os.time())
local offsetX = rng:NextNumber(0, 1000)
local offsetZ = rng:NextNumber(0, 1000)

local terrain = workspace.Terrain
local half = CONFIG.Size / 2

-- Очистка старой карты
terrain:Clear()
local old = workspace:FindFirstChild("Map")
if old then
	old:Destroy()
end
local mapFolder = Instance.new("Folder")
mapFolder.Name = "Map"
mapFolder.Parent = workspace

----------------------------------------------------------------------
-- Высота рельефа
----------------------------------------------------------------------
local function heightAt(x: number, z: number): number
	local s = CONFIG.NoiseScale
	local n1 = math.noise(x * s + offsetX, z * s + offsetZ, 0)
	local n2 = math.noise(x * s * 3 + offsetX, z * s * 3 + offsetZ, 10) * 0.25
	local raw = math.clamp(n1 + n2 + 0.5, 0, 1)

	local d = math.sqrt(x * x + z * z)
	-- 1 в центре, 0 на краю -> остров окружён водой
	local falloff = 1 - math.clamp(d / half, 0, 1) ^ 2

	local h = raw * CONFIG.MaxHeight * falloff + falloff * 8 - 4
	h = math.max(h, -4)

	-- плавный переход к ровной площадке спавна
	local t = math.clamp((d - CONFIG.SpawnRadius) / 16, 0, 1)
	return CONFIG.SpawnHeight + (h - CONFIG.SpawnHeight) * t
end

local function materialAt(h: number): Enum.Material
	if h < CONFIG.WaterLevel + 2 then
		return Enum.Material.Sand
	elseif h < CONFIG.MaxHeight * 0.55 then
		return Enum.Material.Grass
	elseif h < CONFIG.MaxHeight * 0.8 then
		return Enum.Material.Rock
	end
	return Enum.Material.Snow
end

----------------------------------------------------------------------
-- Рельеф и вода
----------------------------------------------------------------------
local BOTTOM = -16

-- Вода одним большим блоком, земля потом перезапишет её там, где выше
terrain:FillBlock(
	CFrame.new(0, (BOTTOM + CONFIG.WaterLevel) / 2, 0),
	Vector3.new(CONFIG.Size, CONFIG.WaterLevel - BOTTOM, CONFIG.Size),
	Enum.Material.Water
)

local cell = CONFIG.Cell
local steps = math.floor(CONFIG.Size / cell)
for i = 0, steps - 1 do
	for j = 0, steps - 1 do
		local x = -half + (i + 0.5) * cell
		local z = -half + (j + 0.5) * cell
		local h = heightAt(x, z)
		terrain:FillBlock(CFrame.new(x, (h + BOTTOM) / 2, z), Vector3.new(cell, h - BOTTOM, cell), materialAt(h))
	end
	if i % 4 == 0 then
		task.wait() -- не вешаем сервер
	end
end

----------------------------------------------------------------------
-- Размещение объектов
----------------------------------------------------------------------
local rayParams = RaycastParams.new()
rayParams.FilterType = Enum.RaycastFilterType.Include
rayParams.FilterDescendantsInstances = { terrain }
rayParams.IgnoreWater = true

local function groundAt(x: number, z: number): RaycastResult?
	return workspace:Raycast(Vector3.new(x, CONFIG.MaxHeight + 50, z), Vector3.new(0, -200, 0), rayParams)
end

local function randomSpot(allowed: { [Enum.Material]: boolean }): (Vector3?, Vector3?)
	for _ = 1, 20 do
		local x = rng:NextNumber(-half * 0.9, half * 0.9)
		local z = rng:NextNumber(-half * 0.9, half * 0.9)
		if math.sqrt(x * x + z * z) > CONFIG.SpawnRadius + 4 then
			local hit = groundAt(x, z)
			if hit and allowed[hit.Material] and hit.Position.Y > CONFIG.WaterLevel then
				return hit.Position, hit.Normal
			end
		end
	end
	return nil, nil
end

local function makePart(props: { [string]: any }): Part
	local p = Instance.new("Part")
	p.Anchored = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	for k, v in props do
		(p :: any)[k] = v
	end
	return p
end

local function makeTree(pos: Vector3)
	local trunkH = rng:NextNumber(8, 14)
	local model = Instance.new("Model")
	model.Name = "Tree"

	local trunk = makePart({
		Name = "Trunk",
		Shape = Enum.PartType.Cylinder,
		Size = Vector3.new(trunkH, 1.6, 1.6),
		-- цилиндр лежит вдоль X, поворачиваем вертикально
		CFrame = CFrame.new(pos + Vector3.new(0, trunkH / 2 - 0.5, 0)) * CFrame.Angles(0, 0, math.pi / 2),
		Material = Enum.Material.Wood,
		Color = Color3.fromRGB(105, 70, 40),
	})
	trunk.Parent = model

	local top = pos + Vector3.new(0, trunkH - 0.5, 0)
	local leafColor = Color3.fromHSV(rng:NextNumber(0.25, 0.34), 0.7, rng:NextNumber(0.45, 0.65))
	for k = 1, 3 do
		local r = rng:NextNumber(5, 8) - k
		local leaf = makePart({
			Name = "Leaves",
			Shape = Enum.PartType.Ball,
			Size = Vector3.new(r, r, r),
			Position = top + Vector3.new(rng:NextNumber(-1.5, 1.5), (k - 1) * 2, rng:NextNumber(-1.5, 1.5)),
			Material = Enum.Material.Grass,
			Color = leafColor,
		})
		leaf.Parent = model
	end

	model.PrimaryPart = trunk
	model.Parent = mapFolder
end

local function makeRock(pos: Vector3, normal: Vector3)
	local size = rng:NextNumber(2, 7)
	local rock = makePart({
		Name = "Rock",
		Size = Vector3.new(size, size * rng:NextNumber(0.6, 1), size * rng:NextNumber(0.8, 1.3)),
		Material = Enum.Material.Slate,
		Color = Color3.fromRGB(110, 110, 115),
	})
	rock.CFrame = CFrame.new(pos + normal * (size * 0.2))
		* CFrame.Angles(rng:NextNumber(0, 6.28), rng:NextNumber(0, 6.28), rng:NextNumber(0, 6.28))
	rock.Parent = mapFolder
end

local grassOnly = { [Enum.Material.Grass] = true }
local rocky = { [Enum.Material.Grass] = true, [Enum.Material.Rock] = true }

for n = 1, CONFIG.TreeCount do
	local pos = randomSpot(grassOnly)
	if pos then
		makeTree(pos)
	end
	if n % 20 == 0 then
		task.wait()
	end
end

for n = 1, CONFIG.RockCount do
	local pos, normal = randomSpot(rocky)
	if pos and normal then
		makeRock(pos, normal)
	end
	if n % 20 == 0 then
		task.wait()
	end
end

----------------------------------------------------------------------
-- Спавн и освещение
----------------------------------------------------------------------
local spawn = Instance.new("SpawnLocation")
spawn.Name = "MapSpawn"
spawn.Anchored = true
spawn.Size = Vector3.new(12, 1, 12)
spawn.Position = Vector3.new(0, CONFIG.SpawnHeight + 0.5, 0)
spawn.Material = Enum.Material.Concrete
spawn.Color = Color3.fromRGB(190, 190, 190)
spawn.TopSurface = Enum.SurfaceType.Smooth
spawn.Parent = mapFolder

Lighting.ClockTime = 14
if not Lighting:FindFirstChildOfClass("Atmosphere") then
	local atmosphere = Instance.new("Atmosphere")
	atmosphere.Density = 0.3
	atmosphere.Parent = Lighting
end

-- Цвет воды
terrain.WaterColor = Color3.fromRGB(40, 120, 160)
terrain.WaterTransparency = 0.8
terrain.WaterWaveSize = 0.15

print(("Карта готова (seed: %s)"):format(tostring(CONFIG.Seed or "random")))
