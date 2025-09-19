interface TextReference {
  reference: string;
  description: string;
}

function stripMarkdownFormatting(text: string): string {
  return text.replace(/\*([^*]+)\*/g, '$1').replace(/\s+/g, ' ').trim();
}

function parseMarkdownReferences(markdown: string): TextReference[] {
  const lines = markdown.split(/\r?\n/);
  const references: TextReference[] = [];
  let current: TextReference | null = null;

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line || line.startsWith('#')) {
      continue;
    }

    const referenceMatch = line.match(/^\d+\.\s+(.*)$/);
    if (referenceMatch) {
      if (current) {
        references.push(current);
      }
      current = {
        reference: stripMarkdownFormatting(referenceMatch[1]),
        description: '',
      };
      continue;
    }

    if (current) {
      const description = stripMarkdownFormatting(line);
      if (description) {
        current.description = current.description
          ? `${current.description} ${description}`
          : description;
      }
    }
  }

  if (current) {
    references.push(current);
  }

  return references;
}

async function loadReferences(): Promise<TextReference[]> {
  const response = await fetch('computer_vision_pipeline_texts.md');
  if (!response.ok) {
    throw new Error(`Failed to load reference list: ${response.status} ${response.statusText}`);
  }

  const markdown = await response.text();
  return parseMarkdownReferences(markdown);
}

document.addEventListener('DOMContentLoaded', async () => {
  const app = document.getElementById('app');
  if (!app) return;

  app.textContent = 'Loading references…';

  try {
    const references = await loadReferences();

    app.textContent = '';

    const heading = document.createElement('h1');
    heading.textContent = 'Top Texts on Computer Vision and Pipeline Architectures';
    app.appendChild(heading);

    const list = document.createElement('ol');
    references.forEach(({ reference, description }) => {
      const item = document.createElement('li');

      const refPara = document.createElement('p');
      refPara.textContent = reference;
      item.appendChild(refPara);

      if (description) {
        const descPara = document.createElement('p');
        descPara.textContent = description;
        item.appendChild(descPara);
      }

      list.appendChild(item);
    });

    app.appendChild(list);
  } catch (error) {
    console.error(error);
    app.textContent = 'Unable to load references. See the Markdown source for the latest list.';
  }
});
