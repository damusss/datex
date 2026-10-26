const {Plugin, PluginSettingTab, Setting, renderMath, finishRenderMath} = require('obsidian');
const {execSync} = require('child_process');

const DEFAULT_SETTINGS = {
    pythonPath: "PYTHON INTERPRETER PATH SETTING NOT SET",
    scriptPath: "SCRIPT PATH SETTING NOT SET"
};

class DaTexToLaTexPlugin extends Plugin {
    constructor(app, manifest) {
        super(app, manifest);
        this.settings = null;
    }

    async onload() {
        await this.loadSettings();

        this.registerMarkdownCodeBlockProcessor("datex", (source, el, ctx) => {
            try {
                const command = `${this.settings.pythonPath} ${this.settings.scriptPath}`;

                const latex = execSync(command, {
                    input: source,
                    encoding: 'utf-8'
                });

                const mathEl = renderMath(latex.trim(), true);
                finishRenderMath();

                if (latex.includes("error")) {
                    mathEl.style.color = "red";
                }

                el.addEventListener("click", (event) => {
                    const embedBlock = el.closest(".cm-embed-block");
                    if (embedBlock) {
                        const editBtn = embedBlock.querySelector(".edit-block-button");
                        if (editBtn) {
                            editBtn.click();
                            event.stopPropagation();
                        }
                    }
                });

                el.appendChild(mathEl);

            } catch (error) {
                const errorEl = el.createEl("div", {
                    text: `Plugin execution error: ${error.message}`
                });

                errorEl.style.color = "red";

                errorEl.addEventListener("click", (event) => {
                    const embedBlock = errorEl.closest(".cm-embed-block");
                    if (embedBlock) {
                        const editBtn = embedBlock.querySelector(".edit-block-button");
                        if (editBtn) {
                            editBtn.click();
                            event.stopPropagation();
                        }
                    }
                });
            }
        });

        this.addSettingTab(new DaTexToLaTexPluginSettingsTab(this.app, this));
    }

    async loadSettings() {
        this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
    }

    async saveSettings() {
        await this.saveData(this.settings);
    }

    onunload() {
    }
}

class DaTexToLaTexPluginSettingsTab extends PluginSettingTab {
    constructor(app, plugin) {
        super(app, plugin);
        this.plugin = plugin;
    }

    display() {
        const {containerEl} = this;

        containerEl.empty();

        containerEl.createEl('h2', {text: 'DaTex to LaTex Plugin Settings'});

        const pythonSetting = new Setting(containerEl)
            .setName('Python interpreter absolute path')
            .setDesc('The absolute path to the python.exe interpreter that will execute the script')
            .addText(text => {
                text.setPlaceholder('Enter absolute path...')
                    .setValue(this.plugin.settings.pythonPath)
                    .onChange(async (value) => {
                        this.plugin.settings.pythonPath = value;
                        await this.plugin.saveSettings();
                    });

                text.inputEl.parentElement.style.width = '100%';
                text.inputEl.style.width = '100%';
            });

        pythonSetting.settingEl.style.flexDirection = 'column';
        pythonSetting.settingEl.style.alignItems = 'stretch';
        pythonSetting.settingEl.style.gap = '10px';


        const scriptSetting = new Setting(containerEl)
            .setName('Obsidian plugin script absolute path')
            .setDesc('The absolute path to the obsidian_plugin_script.py file')
            .addText(text => {
                text.setPlaceholder('Enter absolute path...')
                    .setValue(this.plugin.settings.scriptPath)
                    .onChange(async (value) => {
                        this.plugin.settings.scriptPath = value;
                        await this.plugin.saveSettings();
                    });

                text.inputEl.parentElement.style.width = '100%';
                text.inputEl.style.width = '100%';
            });

        scriptSetting.settingEl.style.flexDirection = 'column';
        scriptSetting.settingEl.style.alignItems = 'stretch';
        scriptSetting.settingEl.style.gap = '10px';
    }

}

module.exports = DaTexToLaTexPlugin;